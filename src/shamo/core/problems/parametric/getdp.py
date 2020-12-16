"""Implement `SolParamGetDP` class."""
from shamo.core.problems.parametric import ProbParamABC
from .components.tissue_property import CompParamTissueProp
from shamo.utils.path import get_relative_path


class ProbParamGetDP(ProbParamABC):
    """A base class for any parametric problem depending on GetDP."""

    def __init__(self, **kwargs):
        self.sigmas = CompParamTissueProp()

    def _gen_py_file(self, prob, name, parent_path, kwargs):
        """Generate a PY file to solve a sub-problem later.

        Parameters
        ----------
        prob : shamo.core.problems.single.ProbABC
            The problem to solve.
        name : str
            The name of the sub-problem.
        parent_path : str, byte or os.PathLike
            The path to the parent directory of the sub-problem.
        kwargs : dict[str, ...]
            Any other arguments.

        Returns
        -------
        list []

        See Also
        --------
        shamo.core.solutions.parametric.SolParam._gen_py_file
        """
        kwargs["model_path"] = str(
            get_relative_path(parent_path, kwargs.get("model", None).json_path)
        )
        return super()._gen_py_file(prob, name, parent_path, kwargs)

    def _solve_sub_probs(
        self, sol, sub_probs, model, method=ProbParamABC.METHOD_SEQ, n_proc=1, **kwargs,
    ):
        """Solve the sub-problems.

        Parameters
        ----------
        sol : shamo.core.solutions.parametric.SolParamABC
            The parametric solution which the sub-solution will be part of.
        sub_prob : shamo.core.problems.single.ProbABC
            The sub-problems to solve.
        model : shamo.FEM
            The finite element model to solve the problem for.
        method : str, optional
            The method to solve the sub-problems. The accepted values are
            ``'sequential'``, ``'multiprocessing'``, ``'job'``. (The default is
            ``'sequential'``)
        n_proc : int, optional
            The number of processes to solve the problem when `method` is set to
            ``'multiprocessing'``. (The default is ``1``)

        See Also
        --------
        shamo.core.solutions.parametric.SolParam._solve_sub_probs

        Notes
        -----
        If `method` is set to ``'job'``, the method will only produce PY files. Each of
        these scripts will solve a sub-problem. Once all the sub-problems are solved,
        one must call `shamo.core.solutions.parametric.SolABC.finalize()` to finalize
        the resolution.
        """
        kwargs["model"] = model
        return super()._solve_sub_probs(sol, sub_probs, method, n_proc, **kwargs)
