from abc import abstractclassmethod

import nib
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
        self["suffix"] = suffix
        x = []
        y = []
        for s in sol.get_sub_sols():
            x.append(sol.get_x(s))
            y.append(metric(cls._get_masked_data(s, suffix, mask)))
        x = np.array(x).reshape((len(sols), -1))
        y = np.array(y).reshape((len(sols),))
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
