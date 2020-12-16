"""Implement `ProbParamEEGLeadfield` class."""
import logging

from shamo.core.problems.parametric import ProbParamGetDP
from shamo.core.problems.single import (
    CompSensors,
    CompTissues,
    CompGridSampler,
    CompFilePath,
)
from shamo.eeg import ProbEEGLeadfield
from .solution import SolParamEEGLeadfield
from shamo.utils.path import get_relative_path

logger = logging.getLogger(__name__)


class ProbParamEEGLeadfield(ProbParamGetDP):
    """A problem definition to solve the parametric EEG forward problem.

    Attributes
    ----------
    sigmas : shamo.core.problems.parametric.CompParamTissueProp
        The electrical conductivity of the tissues.
    markers : shamo.core.problems.single.CompSensors
        The electrodes to ignore when solving the problem.
    reference : shamo.core.problems.single.CompSensors
        The electrode to use as the reference.
    rois : shamo.core.problems.single.CompTissues
        The tissues in which the leadfield must be computed.
    elems_path : shamo.core.problems.single.CompFilePath
        The path to the elements subset.
    grid : shamo.core.problems.single.CompGridSampler
        The grid sampler if the source space must be based on a grid.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._source = CompSensors()
        self.markers = CompSensors()
        self.reference = CompSensors()
        self.rois = CompTissues()
        self.elems_path = CompFilePath()
        self.grid = CompGridSampler()

    @property
    def template(self):
        """Return the name of the template PY file.

        Returns
        -------
        str
            The name of the template PY file.
        """
        return "eeg_leadfield.tmplt"

    def solve(
        self,
        name,
        parent_path,
        model,
        n_evals,
        method="sequential",
        n_proc=1,
        skip=0,
        **kwargs,
    ):
        """Solve the EEG parametric forward problem.

        Parameters
        ----------
        name : str
            The name of the solution.
        parent_path : str, byte or os.PathLike
            The path to the parent directory of the solution.
        model : shamo.fem.FEM
            The finite element model to solve the problem for.
        n_evals : int
            The number of evaluation points.
        method : str, optional
            The method to solve the sub-problems. The accepted values are
            ``'sequential'``, ``'multiprocessing'``, ``'job'``. (The default is
            ``'sequential'``)
        n_proc : int, optional
            The number of processes to solve the problem when `method` is set to
            ``'multiprocessing'``. (The default is ``1``)
        skip : int, optional
            The number of points to skip at the beginning of the sequence. (The default
            is ``0``)

        Returns
        -------
        shamo.eeg.SolParamEEGLeadfield
            The parametric EEG leafield object.
        """
        logger.info("Solving problem")
        self._check_components(**model, **kwargs)
        params = self._gen_params(n_evals, skip, **kwargs)
        base_path = f"{parent_path}/{name}" if method == "jobs" else "."
        sub_probs = self._gen_sub_probs(
            n_evals, parent_path=base_path, **params, **kwargs
        )
        sol = SolParamEEGLeadfield(
            name,
            parent_path,
            markers=self.markers["sensors"],
            reference=self.reference["sensors"],
            rois=self.rois["tissues"],
            sigmas=self.sigmas,
            use_grid=self.grid.use_grid,
        )
        sol["model_json_path"] = str(sol.get_relative_path(model.json_path))
        sub_sols = self._solve_sub_probs(
            sol, sub_probs, method=method, n_proc=n_proc, model=model, **kwargs
        )
        return sol

    def _gen_fixed_varying(self, **kwargs):
        """Generate two lists containing the fixed and varying parameters.

        Returns
        -------
        list [dict {str, ...}]
            The fixed parameters.
        list [dict {str, ...}]
            The varying parameters.
        """
        return self.sigmas.to_param("sigmas", **kwargs)

    def _gen_sub_prob(self, i, **kwargs):
        """Generate one sub-problem.

        Parameters
        ----------
        i : int
            The index of the sub-problem.

        Returns
        -------
        shamo.eeg.ProbEEGLeadfield
            The generated sub-problem.

        Other Parameters
        ----------------
        sigmas : dict [str, list[numpy.ndarray, str]]
            The electrical conductivity of the tissues.
        """
        s = kwargs.get("sigmas", {})
        prob = ProbEEGLeadfield()
        for t, p in s.items():
            prob.sigmas.set(t, p[0][i], p[1])
        prob.reference = self.reference
        prob.markers = self.markers
        prob.rois = self.rois
        if self.elems_path.use_path:
            prob.elems_path.set(
                get_relative_path(kwargs.get("parent_path", "."), self.elems_path.path)
            )
        prob.grid = self.grid
        return prob

    def _check_components(self, **kwargs):
        """Check if the components are properly set."""
        self.sigmas.check("sigmas", **kwargs)
        self._source.check("source", **kwargs)
        self.reference.check("reference", **kwargs)
        self.rois.check("region of interest", **kwargs)
        self.elems_path.check("elements path", **kwargs)
        self.grid.check("grid", **kwargs)
        if self.elems_path.use_path and self.grid.use_grid:
            raise RuntimeError(
                "Both 'elems_path' and 'grid' are set. Only one of them is allowed."
            )
