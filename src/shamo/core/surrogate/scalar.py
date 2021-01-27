"""Implement `SurrScalar` class."""
import json

from SALib.sample import saltelli
from SALib.analyze import sobol

from .abc import SurrABC


class SurrScalar(SurrABC):
    """Generate a Gaussian process from a set of scalar training data.

    Parameters
    ----------
    name : str
        The name of the generated surrogate model.
    parent_path : str, byte or os.PathLike
        The path to the parent directory of the surrogate model.

    Other Parameters
    ----------------
    params : list [tuple [str, shamo.DistABC]]
        A list of tuples containing the names of the parameters and the
        corresponding distributions as values.
    sol_json_path : str
        The path to the parametric solution the surrogate is built of.
    is_sobol_available : bool
        If ``True``, Sobol indices are already available.

    See Also
    --------
    shamo.core.surrogate.SurrABC
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        self.update({"is_sobol_available": kwargs.get("is_sobol_available", False)})

    @property
    def is_sobol_available(self):
        """Return whether the Sobol indices are already computed.

        Returns
        -------
        bool
            Return ``True`` if the indices are already computed, ``False`` otherwise.
        """
        return self["is_sobol_available"]

    @property
    def sobol_path(self):
        """Return the path to the file storing the Sobol indices.

        Returns
        -------
        pathlib.Path
            The path to the file storing the Sobol indices.
        """
        return self.path / f"{self.name}_sobol.json"

    def get_sobol(self):
        """Return the precomputed Sobol indices.

        Returns
        -------
        dict [str, list [str]|dict [str, float]]|None
            A dictionary containing the names of the parameters, the values of the
            first, second and total order Sobol indices and the corresponding
            confidence with respect to the `conf_level`.
            If the file does not exist, returns ``None``.
        """
        if self.is_sobol_available:
            with open(self.sobol_path, "r") as f:
                return json.load(f)
        return None

    def gen_sobol(self, n=1000, n_resamples=100, conf_level=0.95):
        """Compute Sobol sensitivity indices.

        Parameters
        ----------
        n : int, optional
            The number of sample to predict with the Gaussian process. The default is
            ``1000``.
        n_resamples : int, optional
            The number of resamples. The default is ``100``.
        conf_level : float, optional
            The confidence interval level. The default is ``0.95``.

        Returns
        -------
        dict [str, list [str]|dict [str, float]]
            A dictionary containing the names of the parameters, the values of the
            first, second and total order Sobol indices and the corresponding
            confidence with respect to the `conf_level`.
        """
        indices = self.get_sobol()
        if indices is not None:
            return sobol
        params_names = [n for n, _ in self.params]
        prob = {
            "num_vars": len(self.params),
            "names": params_names,
            "dists": [d.salib_name for _, d in self.params],
            "bounds": [d.salib_bounds for _, d in self.params],
        }
        x = saltelli.sample(prob, n)
        y, _ = self.predict(x)
        s_i = sobol.analyze(prob, y, num_resamples=n_resamples, conf_level=conf_level)
        indices = {
            "params": params_names,
            "s1": {"val": s_i["S1"].tolist(), "conf": s_i["S1_conf"].tolist()},
            "s2": {"val": s_i["S2"].tolist(), "conf": s_i["S2_conf"].tolist()},
            "st": {"val": s_i["ST"].tolist(), "conf": s_i["ST_conf"].tolist()},
        }
        with open(self.sobol_path, "w") as f:
            json.dump(indices, f, indent=4, sort_keys=True)
        self["is_sobol_available"] = True
        self.save()
        return indices
