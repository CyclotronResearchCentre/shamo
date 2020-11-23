"""Implement `SurrEEGLeadfieldDifToRef` class."""
import numpy as np

from shamo.core.surrogate import SurrScalar


class SurrEEGLeadfieldDifToRef(SurrScalar):
    """Provide a wayto evaluate the sensitivity of the EEG leadfield.

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
    shamo.core.surrogate.SurrScalar
    """

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
        list [tuple [str, shamo.DistABC]]
            A list of tuples containing the names of the parameters and the
            corresponding distributions as values.
        """
        ref = kwargs.get("ref", None)
        m_ref = np.array(ref.get_matrix())
        params = [
            [t, d[0]] for t, d in sol.sigmas.items() if d[0].dist_type != "constant"
        ]
        sols = sol.get_sub_sols()
        x = []
        y = []
        for s in sols:
            x.append([s.sigmas[t][0] for t, _ in params])
            m = s.get_matrix()
            y.append(np.linalg.norm(m - m_ref, "fro"))
        x = np.array(x)
        y = np.array(y)
        return x, y, params

    @classmethod
    def _check_params(cls, **kwargs):
        """Check if the parameters are properly set.

        Raises
        ------
        RuntimeError
            If the argument `ref` is not given.
        """
        if kwargs.get("ref", None) is None:
            raise RuntimeError("Missing 'ref' argument.")
