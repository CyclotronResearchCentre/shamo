"""Implement `ProbParamABC` class."""
from abc import abstractmethod, abstractproperty
import itertools as iter
import logging
import multiprocessing as mp
from pathlib import Path
import re

import chaospy as chaos
from jinja2 import Environment, PackageLoader
import numpy as np

from shamo.core.problems.single import ProbABC

logger = logging.getLogger(__name__)


class ProbParamABC(ProbABC):
    """A base class for any parametric problem."""

    METHOD_SEQ = "sequential"
    METHOD_MUL = "multiprocessing"
    METHOD_JOB = "job"

    @abstractproperty
    def template(self):
        """Return the path to the template PY file."""

    @abstractmethod
    def _gen_fixed_varying(self, **kwargs):
        """Generate two lists containing the fixed and varying parameters.

        Returns
        -------
        list [dict {str, ...}]
            The fixed parameters.
        list [dict {str, ...}]
            The varying parameters.
        """

    def _gen_params(self, n_evals, skip=0, **kwargs):
        """Generate the evaluation points.

        Parameters
        ----------
        n_evals : int
            The number of points to generate.
        skip : int, optional
            The number of points to skip at the beginning of the sequence. (The default
            is ``0``)

        Returns
        -------
        dict [str, dict[str, numpy.ndarray]]
            The evaluation points.

        Raises
        ------
        RuntimeError
            If no parameter is set as a random variable.

        Notes
        -----
        The parameters space is sampled by first modelling each random variable as a
        uniform distribution and then drawing the points from a Halton quasi-random
        sequence.

        This allows for a better covering of the whole space than if the actual
        distributions were used for each random input.
        """
        fixed, varying = self._gen_fixed_varying(**kwargs)
        if len(varying) == 0:
            raise RuntimeError(
                "No varying parameter was found. Use 'ProbEEGLeadfield' instead."
            )
        dist = chaos.J(*[p[0].uniform_dist for _, p in varying])
        x = dist.sample(n_evals + skip, rule="halton").reshape((len(dist), -1))
        if skip != 0:
            x = x[:, skip:]
        params = {}
        for i, (n, p) in enumerate(varying):
            prop, name = ProbParamABC._split_prop_name(n)
            if prop not in params:
                params[prop] = {}
            params[prop][name] = [x[i, :].ravel(), p[1]]
        for n, p in fixed:
            prop, name = ProbParamABC._split_prop_name(n)
            if prop not in params:
                params[prop] = {}
            params[prop][name] = [np.ones((x.shape[1],)) * p[0], p[1]]
        return params

    @staticmethod
    def _split_prop_name(name):
        """Split the names of the parameters."""
        match = re.match(r"^(?P<prop>[a-zA-Z]+)\.(?P<name>\w+)$", name)
        return match.group("prop"), match.group("name")

    @abstractmethod
    def _gen_sub_prob(self, i, **kwargs):
        """Generate one sub-problem.

        Parameters
        ----------
        i : int
            The index of the sub-problem.

        Returns
        -------
        shamo.core.problems.single.ProbABC
            The generated sub-problem.
        """

    @abstractmethod
    def _gen_sub_probs(self, n_evals, **kwargs):
        """Generate all the sub-problems.

        Parameters
        ----------
        n_evals : int
            The number of evaluation points.
        """
        return [self._gen_sub_prob(i, **kwargs) for i in range(n_evals)]

    def _solve_sub_prob(self, problem, name, parent_path, kwargs):
        """Solve one sub-problem.

        Parameters
        ----------
        problem : shamo.core.problems.single.ProbABC
            The sub-problem to solve.
        name : str
            The name of the sub-problem.
        parent_path : str, byte or os.PathLike
            The path to the parent directory of the sub-problem.
        kwargs : dict[str, ...]
            Any other arguments.

        Returns
        -------
        shamo.core.objects.ObjDir
            The solution to the problem.
        """
        return problem.solve(name, parent_path, **kwargs)

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
        """
        logger.info("Generating python files.")
        env = Environment(loader=PackageLoader("shamo", "templates/py"))
        template = env.get_template(self.template)
        content = template.render(
            problem=prob,
            name=name,
            parent_path=str(parent_path),
            **kwargs,
            **prob._prepare_py_file_params(**kwargs),
        )
        with open(Path(parent_path) / f"{name}.py", "w") as f:
            f.write(content)
        return []

    def _solve_sub_probs(
        self, sol, sub_probs, method="sequential", n_proc=1, **kwargs,
    ):
        """Solve the sub-problems.

        Parameters
        ----------
        sol : shamo.core.solutions.parametric.SolParamABC
            The parametric solution which the sub-solution will be part of.
        sub_probz : shamo.core.problems.single.ProbABC
            The sub-problemz to solve.
        method : str, optional
            The method to solve the sub-problems. The accepted values are
            ``'sequential'``, ``'multiprocessing'``, ``'job'``. (The default is
            ``'sequential'``)
        n_proc : int, optional
            The number of processes to solve the problem when `method` is set to
            ``'multiprocessing'``. (The default is ``1``)

        Notes
        -----
        If `method` is set to ``'job'``, the method will only produce PY files. Each of
        these scripts will solve a sub-problem. Once all the sub-problems are solved,
        one must call `shamo.core.solutions.parametric.SolABC.finalize()` to finalize
        the resolution.
        """
        logger.info(f"Solving {len(sub_probs)} sub-problems.")
        generator = (
            [p, f"{sol.name}_{i:08d}", sol.path, kwargs]
            for i, p in enumerate(sub_probs)
        )
        sub_sols = []
        if method == self.METHOD_SEQ:
            sub_sols = list(iter.starmap(self._solve_sub_prob, generator))
            sol.finalize(**kwargs)
        elif method == self.METHOD_MUL:
            with mp.Pool(processes=n_proc) as p:
                sub_sols = list(p.starmap(self._solve_sub_prob, generator))
            sol.finalize(**kwargs)
        else:
            sub_sols = list(iter.starmap(self._gen_py_file, generator))
        return sub_sols

    @abstractmethod
    def solve(
        self,
        name,
        parent_path,
        n_evals,
        method="sequential",
        n_proc=1,
        skip=0,
        **kwargs,
    ):
        """Solve the parametric problem.

        Parameters
        ----------
        name : str
            The name of the solution.
        parent_path : str, byte or os.PathLike
            The path to the parent directory of the solution.
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
        shamo.core.solutions.parametric.SolParamABC
            The generated solution.
        """
