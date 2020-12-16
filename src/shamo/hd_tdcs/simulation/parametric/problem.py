"""Implement `ProbParamHDTDCSSim` class."""
import logging

from shamo.core.problems.parametric import ProbParamGetDP, CompParamValue
from shamo.core.problems.single import CompGridSampler, CompSensors
from shamo.hd_tdcs import ProbHDTDCSSim
from .solution import SolParamHDTDCSSim

logger = logging.getLogger(__name__)


class ProbParamHDTDCSSim(ProbParamGetDP):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid = CompGridSampler()
        self.references = CompSensors()
        self.source = CompSensors()
        self.current = CompParamValue()

    @property
    def template(self):
        """Return the name of the template PY file.

        Returns
        -------
        str
            The name of the template PY file.
        """
        return "hdtdcs_simulation.tmplt"

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
        """Simulate a parametric HD-tDCS.

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
        shamo.hd_tdcs.SolParamHDTDCSSim
            The parametric HD-tDCS solution.
        """
        logger.info("Solving problem")
        self._check_components(**model, **kwargs)
        params = self._gen_params(n_evals, skip, **kwargs)
        sub_probs = self._gen_sub_probs(n_evals, **params, **kwargs)
        sol = SolParamHDTDCSSim(
            name,
            parent_path,
            references=self.references["sensors"],
            source=self.source["sensors"][0],
            current=self.current["val"],
            sigmas=self.sigmas,
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
        fix_sigmas, var_sigmas = self.sigmas.to_param("sigmas", **kwargs)
        fix_current, var_current = self.current.to_param("current", **kwargs)
        return [*fix_sigmas, *fix_current], [*var_sigmas, *var_current]

    def _check_components(self, **kwargs):
        """Check if the components are properly set."""
        self.grid.check("grid", **kwargs)
        self.source.check("source", **kwargs)
        self.references.check("references", **kwargs)
        self.current.check("current", **kwargs)

    def _gen_sub_prob(self, i, **kwargs):
        """Generate one sub-problem.

        Parameters
        ----------
        i : int
            The index of the sub-problem.

        Returns
        -------
        shamo.hd_tdcs.ProbHDTDCSSim
            The generated sub-problem.

        Other Parameters
        ----------------
        sigmas : dict [str, list[numpy.ndarray, str]]
            The electrical conductivity of the tissues.
        """
        s = kwargs.get("sigmas", {})
        prob = ProbHDTDCSSim()
        for t, p in s.items():
            prob.sigmas.set(t, p[0][i], p[1])
        prob.references = self.references
        prob.source = self.source
        c = kwargs.get("current", {})
        prob.current = c["val"][0][i]
        prob.grid = self.grid
        return prob
