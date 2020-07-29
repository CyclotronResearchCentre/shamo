"""Implement `EEGParametricForwardProblem` class.

This module implements the `EEGParametricForwardProblem` class which provides a
solver for the EEG parametric forward problem.
"""
import itertools as iter
import multiprocessing as mp
from pathlib import Path
from pkg_resources import resource_filename

import chaospy as cp

from shamo import EEGForwardProblem
from shamo.utils import TemplateFile, get_relative_path


class EEGParametricForwardProblem(EEGForwardProblem):
    """Provide a solver for the EEG forward problem.

    Parameters
    ----------
    regions_of_interest : list [str]
        The names of the regions of interest.
    markers : list [str]
        The names of the markers.
    electrical_conductivity : dict [str, dict]
        The electrical conductivity of the tissues [S/m].
    reference : str
        The name of the reference sensor.

    See Also
    --------
    shamo.problems.eeg.forward.eeg_forward_problem.EEGForwardProblem
    """

    METHOD_SEQ = "seq"
    METHOD_MULTI = "multi"
    METHOD_MPI = "mpi"
    METHOD_JOBS = "jobs"

    SUB_PROBLEM_FACTORY = EEGForwardProblem

    TEMPLATE_PATH = resource_filename(
        "shamo", str(Path("problems/forward/eeg/eeg_forward_problem.template"))
    )

    def solve(self, name, parent_path, model, **kwargs):
        """Solve the problem.

        Parameters
        ----------
        name : str
            The name of the solution.
        parent_path : PathLike
            The path to the parent directory of the solution.
        model : shamo.core.objects.FileObject
            The model to solve the problem on.

        Other Parameters
        ----------------
        n_evals : int
            The number of points to generate.
        skip : int
            If set to a value different from ``0``, the Halton sequence skips the `skip`
            first points.

        Returns
        -------
        shamo.solutions.forward.eeg.eeg_forward_solution.EEGForwardSolution
            The solution of the problem for the specified model.
        """
        from shamo import EEGParametricForwardSolution

        self.check_settings(model)
        # Initialize the solution
        solution = EEGParametricForwardSolution(name, parent_path)
        solution.set_problem(self)
        solution.set_model(model)
        solution.save()
        # Generate evaluation points
        n_evals = kwargs.get("n_evals", 20)
        skip = kwargs.get("skip", 0)
        eval_points = self._generate_evaluation_points(n_evals)
        # Generate problems
        sub_problems = self._generate_sub_problems(n_evals, eval_points)
        generator = (
            (problem, "sol_{:08d}".format(i), solution.path, model)
            for i, problem in enumerate(sub_problems)
        )
        # Solve using the right method
        method = kwargs.get("method", self.METHOD_SEQ)
        n_process = kwargs.get("n_process", None)
        if method == self.METHOD_SEQ or n_process == 1:
            solutions = list(iter.starmap(self._solve_single_sub_problem, generator))
            solution.finalize()
        elif method == self.METHOD_MULTI:
            with mp.Pool(processes=n_process) as pool:
                solutions = list(
                    pool.starmap(self._solve_single_sub_problem, generator)
                )
            solution.finalize()
        elif method == self.METHOD_MPI:
            pass
        else:
            solutions = list(iter.starmap(self._print_single_sub_problem, generator))
        # Check if all the solutions or scripts were generated
        if len(solutions) != n_evals:
            raise RuntimeError("Some solutions were not computed.")
        return solution

    def _generate_evaluation_points(self, n_evals, skip=0):
        """Generate the coordinates of the points to evaluate.

        Parameters
        ----------
        n_evals : int
            The number of points to generate.
        skip : int
            If set to a value different from ``0``, the Halton sequence skips the `skip`
            first points. (The default is ``0``)

        Returns
        -------
        dict [str, float|numpy.ndarray]
            The points to evaluate.
        """
        tissue_distributions = [
            (name, tissue.value.distribution)
            for name, tissue in self.electrical_conductivity.items()
        ]
        # Only consider non constant parameters
        varying = [item for item in tissue_distributions if item[1] is not None]
        if len(varying) == 0:
            raise RuntimeError(
                ("No varying parameter given. Use " "'EEGForwardProblem' instead.")
            )
        distribution = cp.J(*[distribution for _, distribution in varying])
        absissas = distribution.sample(n_evals, rule="halton")
        if skip != 0:
            absissas = absissas[:, skip:]
        points = {
            varying[i][0]: absissas[i, :].flatten().tolist()
            for i in range(len(varying))
        }
        for name, _ in [item for item in tissue_distributions if item[1] is None]:
            points[name] = self.electrical_conductivity[name].value.value
        return points

    def _generate_sub_problems(self, n_evals, eval_points):
        """Generate a problem for each evaluation point.

        Parameters
        ----------
        n_evals : int
            The number of evaluation points.
        eval_points : dict [str, float|numpy.ndarray]
            The coordinates of the evaluation points.

        Returns
        -------
        list [shamo.problems.forward.eeg.eeg_forward_problem.EEGForwardProblem]
            The generated problems.
        """
        sub_problems = []
        for i_problem in range(n_evals):
            sub_problem = self.SUB_PROBLEM_FACTORY()
            sub_problem.set_reference(self.reference)
            sub_problem.add_markers(self.markers)
            sub_problem.add_regions_of_interest(self.regions_of_interest)
            for name, values in eval_points.items():
                anisotropy = self.electrical_conductivity[name].anisotropy
                value = 0
                try:
                    value = values[i_problem]
                except TypeError:
                    value = values
                sub_problem.set_electrical_conductivity(name, value, anisotropy)
            sub_problems.append(sub_problem)
        return sub_problems

    @staticmethod
    def _solve_single_sub_problem(problem, name, parent_path, model):
        """Solve one sub-problem.

        Parameters
        ----------
        name : str
            The name of the sub-solution.
        parent_path : PathLike
            The path to the parent directory of the sub-solution.
        model : shamo.model.fe_model.FEModel
            The model used to solve the problem.

        Returns
        -------
        shamo.solutions.forward.eeg.eeg_forward_solution.EEGForwardSolution
            The sub-solution.
        """
        return problem.solve(name, parent_path, model)

    @staticmethod
    def _print_single_sub_problem(problem, name, parent_path, model):
        """Generate a script which can be used to solve one sub-problem.

        Parameters
        ----------
        problem : shamo.EEGForwardProblem
            The sub-problem.
        name : str
            The name of the sub-solution.
        parent_path : PathLike
            The path to the parent directory of the sub-solution.
        model : shamo.model.fe_model.FEModel
            The model used to solve the problem.

        Returns
        -------
        PathLike
            The path to the generated script.
        """
        path = str(Path(parent_path) / "{}.py".format(name))
        with TemplateFile(
            EEGParametricForwardProblem.TEMPLATE_PATH, path
        ) as template_file:
            model_path = get_relative_path(model.json_path, parent_path)
            template_file.replace_with_text("model", "path", model_path)
            template_file.replace_with_text("problem", "data", str(problem))
            template_file.replace_with_text("solution", "name", name)
        return str(Path(path).relative_to(parent_path))
