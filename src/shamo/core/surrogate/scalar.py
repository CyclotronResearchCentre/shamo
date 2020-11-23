"""Implement `SurrScalar` class."""
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

    See Also
    --------
    shamo.core.surrogate.SurrABC
    """

    def gen_sobol_indices(self, n=1000, n_resamples=100, conf_level=0.95):
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
        numpy.ndarray
            The first order Sobol indices.
        numpy.ndarray
            The confidence in the first ordr Sobol indices.
        numpy.ndarray
            The second order Sobol indices.
        numpy.ndarray
            The confidence in the second ordr Sobol indices.
        numpy.ndarray
            The total order Sobol indices.
        numpy.ndarray
            The confidence in the total ordr Sobol indices.
        """
        print(self.params)
        prob = {
            "num_vars": len(self.params),
            "names": [n for n, _ in self.params],
            "dists": [d.salib_name for _, d in self.params],
            "bounds": [d.salib_bounds for _, d in self.params],
        }
        x = saltelli.sample(prob, n)
        y, _ = self.predict(x)
        s_i = sobol.analyze(prob, y, num_resamples=n_resamples, conf_level=conf_level)
        return (
            s_i["S1"],
            s_i["S1_conf"],
            s_i["S2"],
            s_i["S2_conf"],
            s_i["ST"],
            s_i["ST_conf"],
        )
