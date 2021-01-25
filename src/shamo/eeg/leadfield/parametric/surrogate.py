"""Implement `SurrEEGLeadfield` and `SurrEEGLeadfieldDifToRef` classes."""
import shutil

import numpy as np

from shamo.core.surrogate import SurrABC, SurrScalar
from shamo.eeg import SolEEGLeadfield, SolParamEEGLeadfield


class SurrEEGLeadfield(SurrABC):
    """Provide a way to generate any leadfield matrix from a set of conductivity.

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

        See Also
        --------
        shamo.core.surrogate.SurrABC
        """
        params = [
            [t, d[0]] for t, d in sol.sigmas.items() if d[0].dist_type != "constant"
        ]
        sols = sol.get_sub_sols()
        x = []
        y = []
        for s in sols:
            x.append([s.sigmas[t][0] for t, _ in params])
            y.append(np.array(s.get_matrix()).ravel())
        x = np.array(x)
        y = np.array(y)
        return x, y, params

    @classmethod
    def _check_params(cls, **kwargs):
        """Check if the parameters are properly set."""
        pass

    def _post_pro(self, x, y_mean, y_std, **kwargs):
        """Reshape the vectors into matrices.

        Parameters
        ----------
        numpy.ndarray
            The evaluation points.
        numpy.ndarray
            The evaluations mean.
        numpy.ndarray
            The evaluations standard deviations.

        Returns
        -------
        numpy.ndarray
            The evaluations mean.
        numpy.ndarray
            The evaluations standard deviations.
        """
        sol = SolParamEEGLeadfield.load(self.sol_json_path)
        shape = (x.shape[0], *sol.shape)
        y_mean_post = np.zeros(shape)
        for i in range(shape[0]):
            y_mean_post[i, :, :] = y_mean[i, :].reshape(shape[1:])
        return y_mean_post, y_std

    def predict_sol(self, name, parent_path, x, skip=0, **kwargs):
        """Generate new `SolEEGLeadfield` by evaluating the Gaussian process.

        Parameters
        ----------
        name : str
            The base name of the generated solution.
        parent_path : str, byte or os.PathLike
            The path to the parent directory of the solution.
        x : numpy.ndarray
            The evaluation points.
        skip : int, optional
            The starting index of the names of the solutions. The default is ``0``.

        Returns
        -------
        list [shamo.eeg.SolEEGLeadfield]
            The generated solutions.
        """
        param_sol = SolParamEEGLeadfield.load(self.sol_json_path)
        sol = SolEEGLeadfield.load(param_sol.sub_json_paths[0])
        sigmas = {t: s for t, s in sol.sigmas.items()}
        y, _ = self.predict(x, **kwargs)
        sols = []
        for i in range(x.shape[0]):
            for j, (t, d) in enumerate(self.params):
                sigmas[t][0] = x[i][j]
            s = SolEEGLeadfield(
                f"{name}_{i + skip:08d}",
                parent_path,
                markers=param_sol.markers,
                reference=param_sol.reference,
                rois=param_sol.rois,
                sensors=param_sol.sensors,
                shape=param_sol.shape,
                sigmas=sigmas,
                use_grid=param_sol.use_grid,
            )
            s["model_json_path"] = str(s.get_relative_path(sol.model_json_path))
            s.set_matrix(y[i, :, :].squeeze())
            shutil.copy(sol.source_sp_path, s.source_sp_path)
            s.save()
            sols.append(s)
        return sols


class SurrEEGLeadfieldToRef(SurrScalar):
    """Provide a way to evaluate the sensitivity of the EEG leadfield.

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
    def _get_data(cls, sol, metric=None, **kwargs):
        """Extract relevant data from a parametric solution.

        Parameters
        ----------
        sol : shamo.core.solutions.parametric.SolParamABC
            The parametric solution to generate a surrogate model for.
        metric : function
            A function taking two parameters. First, the reference matrix and second the
            leadfield matrix considered. It must return a single scalar.

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
        sols = sol.get_sub_sols()
        x = []
        y = []
        for s in sols:
            x.append(sol.get_x(s))
            m = s.get_matrix()
            y.append(metric(m_ref, m))
        x = np.array(x).reshape((len(sols), -1))
        y = np.array(y).reshape((len(sols),))
        return x, y, sol.get_params()

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
