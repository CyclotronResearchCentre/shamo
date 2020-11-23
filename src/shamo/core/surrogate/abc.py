"""Implement the `SurrABC` class."""
from abc import abstractclassmethod
import pickle

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel

from shamo.core.objects import ObjDir
from shamo import DistABC


class SurrABC(ObjDir):
    """Generate a Gaussian process from a set of training data.

    Parameters
    ----------
    name : str
        The name of the generated surrogate model.
    parent_path : str, byte or os.PathLike
        The path to the parent directory of the surrogate model.

    Other Parameters
    ----------------
    params : dict [str, shamo.DistABC]
        A dict containing the names of the parameters as keys and the corresponding
        distributions as values.
    sol_json_path : str
        The path to the parametric solution the surrogate is built of.
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path)
        self.update(
            {
                "params": {
                    n: DistABC.load(d) for n, d in kwargs.get("params", {}).items()
                },
                "sol_json_path": kwargs.get("sol_json_path", None),
            }
        )

    @property
    def gp_path(self):
        """Return the path of the Gaussian process file.

        Returns
        -------
        pathlib.Path
            The path of the Gaussian process file.
        """
        return self.path / f"{name}.gp"

    @property
    def sol_json_path(self):
        return (self.path / self["sol_json_path"]).resolve()

    @property
    def params(self):
        """Return the parameters of the surrogate model.

        Returns
        -------
        dict [str, shamo.DistABC]
            The the parameters of the surrogate model.
        """
        return self["params"]

    @classmethod
    def _get_data(cls, sol, **kwargs):
        """Extract relevant data from a parametric solution.

        Parameters
        ----------
        sol : shamo.core.solutions.parametric.SolParamABC
            The parametric solution to generate a surrogate model for.

        Returns
        -------
        numpy.ndarray
            The coordinates of the training points in the parameter space. Each row
            represents an evaluation.
        numpy.ndarray
            The observations of the actual model at each coordinate from `x`. Each row
            represents an observation.
        dict [str, shamo.DistABC]
            A dict containing the names of the parameters as keys and the corresponding
            distributions as values.

        Notes
        -----
        This method must be implemented to be able to generate a surrogate model.
        """

    @classmethod
    def fit(cls, name, parent_path, sol, **kwargs):
        """Generate a Gaussian process from a set of training data.

        Parameters
        ----------
        name : str
            The name of the generated surrogate model.
        parent_path : str, byte or os.PathLike
            The path to the parent directory of the surrogate model.
        sol : shamo.core.solutions.parametric.SolParamABC
            The parametric solution to generate a surrogate model for.

        Returns
        -------
        shamo.Surrogate
            The generated surrogate model.

        Other Parameters
        ----------------
        kernel : sklearn.gaussian_process.kernels.Kernel
            The kernel used to generate the Gaussian process.
        n_restarts_optimizer : int
            The number of restarts for the optimisation step.
        random_state : int
            The seed for the random state.
        alpha : float
            The added diagonal to account for noise on training points.

        See Also
        --------
        sklearn.gaussian_process.GaussianProcessRegressor
        """
        x, y, params = cls._get_data(sol, **kwargs)
        kernel = kwargs.get(
            "kernel",
            ConstantKernel() * Matern(length_scale=[1.0] * len(params), nu=1.5),
        )
        n_restarts_optimizer = kwargs.get("n_restarts_optimizer", 0)
        random_state = kwargs.get("random_state", 0)
        alpha = kwargs.get("alpha", 1e-10)
        gp = GaussianProcessRegressor(
            kernel=kernel,
            n_restarts_optimizer=n_restarts_optimizer,
            random_state=random_state,
            normalize_y=True,
            alpha=alpha,
        ).fit(x, y)
        surr = cls(name, parent_path, params=params)
        surr["sol_json_path"] = surr.get_relative_path(sol.json_path)
        pickle.dump(gp, open(surr.gp_path, "wb"))
        surr.save()
        return surr

    def get_gp(self):
        """Load the Gaussian process.

        Returns
        -------
        sklearn.gaussian_process.GaussianProcessRegressor
            The Gaussian process.
        """
        return pickle.load(open(self.gp_path, "rb"))

    def predict(self, x, **kwargs):
        """Evaluate the Gaussian process on new points.

        Parameters
        ----------
        x : numpy.ndarray
            The coordinates of the evaluation points in the parameter space. Each row
            represents an evaluation.

        Notes
        -----
        To change the behaviour of this method, one should subclass `Surrogate` and
        change the `_post_pro` method.
        """
        gp = self.get_gp()
        y_mean, y_std = gp.predict(x, return_std=True)
        return self._post_pro(x, y_mean, y_std, **kwargs)

    def _post_pro(self, x, y_mean, y_std, **kwargs):
        """Applies a post-processing operation to the predictions.

        Returns
        -------
        numpy.ndarray
            The evaluations mean.
        numpy.ndarray
            The evaluations standard deviations.

        Notes
        -----
        This method should be modified to apply post-processing operations.
        """
        return y_mean, y_std
