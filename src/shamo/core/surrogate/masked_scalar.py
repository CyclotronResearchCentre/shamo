from abc import abstractclassmethod

import nibabel as nib
import numpy as np

from shamo.core.surrogate import SurrScalar


class SurrMaskedScalar(SurrScalar):
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
    suffix : str
        The suffix appended to the queried files.

    See Also
    --------
    shamo.core.surrogate.SurrScalar
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        self.update({"suffix": kwargs.get("suffix", "")})

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
        n_proc : int
            The number of jobs to run in parallel. ``None`` means 1 job runs at a time
            and ``-1`` means all cores are used.
        metric : func
            The metric to compute.
        suffix : str
            The suffix to append to the file query.

        See Also
        --------
        sklearn.gaussian_process.GaussianProcessRegressor
        """
        surr = super().fit(name, parent_path, sol, **kwargs)
        surr["suffix"] = kwargs.get("suffix", "")
        surr.save()
        return surr

    @classmethod
    def _get_data(cls, sol, suffix="", metric=None, mask=None, **kwargs):
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
        list [tuple [str, shamo.DistABC]]
            A list of tuples containing the names of the parameters and the
            corresponding distributions as values.

        Other Parameters
        ----------------
        suffix : str
            The suffix to append to the queried files.
        metric : func
            A function to run on the masked data. It must take one parameter.
        mask : numpy.ndarray
            The mask to apply to the data.

        See Also
        --------
        shamo.core.surrogate.SurrABC
        """
        x = []
        y = []
        for s in sol.get_sub_sols():
            x.append(sol.get_x(s))
            y.append(metric(cls._get_masked_data(s, suffix, mask)))
        x = np.array(x).reshape((len(x), -1))
        y = np.array(y).reshape((len(y),))
        return x, y, sol.get_params()

    @abstractclassmethod
    def _get_masked_data(cls, sol, suffix, mask):
        """Return a linear array containing the masked data.

        Parameters
        ----------
        sol : shamo.core.solutions.single.SolABC
            A solution.
        suffix : str
            The suffix appended to the filename without the extension.
        mask : numpy.ndarray
            A boolean numpy array used to mask the data.

        Returns
        -------
        numpy.ndarray
            The masked data.
        """


class SurrMaskedScalarNii(SurrMaskedScalar):
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
    suffix : str
        The suffix appended to the queried files.

    See Also
    --------
    shamo.core.surrogate.SurrMaskedScalar
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
        n_proc : int
            The number of jobs to run in parallel. ``None`` means 1 job runs at a time
            and ``-1`` means all cores are used.
        metric : func
            The metric to compute.
        suffix : str
            The suffix to append to the file query.
        mask : nibabel.Nifti1Image
            A NIFTI image to use as a mask.

        See Also
        --------
        sklearn.gaussian_process.GaussianProcessRegressor
        """
        mask = kwargs.pop("mask")
        data = mask.get_fdata().astype(bool)
        surr = super().fit(name, parent_path, sol, mask=data, **kwargs)
        mask.to_filename(surr.path / f"{surr.name}_mask.nii")
        return surr

    @classmethod
    def _get_masked_data(cls, sol, suffix, mask):
        """Return a linear array containing the masked data.

        Parameters
        ----------
        sol : shamo.core.solutions.single.SolABC
            A solution.
        suffix : str
            The suffix appended to the filename without the extension.
        mask : numpy.ndarray
            A boolean numpy array used to mask the data.

        Returns
        -------
        numpy.ndarray
            The masked data.
        """
        img = nib.load(sol.path / f"{sol.name}_{suffix}.nii")
        return img.get_fdata()[mask]
