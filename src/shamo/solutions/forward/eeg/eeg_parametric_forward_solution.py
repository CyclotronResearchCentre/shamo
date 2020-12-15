"""Implement `EEGParametricForwardSolution` class.

This module implements the `EEGParametricForwardSolution` class which holds the
data corresponding to the solution of the EEG parametric forward problem.
"""
import itertools as iter
import multiprocessing as mp
from pathlib import Path
import pickle
from tempfile import TemporaryDirectory

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor, kernels
from sklearn.multioutput import MultiOutputRegressor

from shamo.solutions import ParametricForwardSolution, MaternProd
from shamo.utils.path import get_relative_path


class EEGParametricForwardSolution(ParametricForwardSolution):
    """The solution to an EEG parametric forward problem.

    Parameters
    ----------
    name : str
        The name of the solution.
    parent_path : str
        The path to the parent directory of the solution.

    Other Parameters
    ----------------
    problem : dict [str, Any]
        The problem that result in this solution.
    model_path : PathLike
        The path to the model file.
    shape : tuple (int, int)
        The shape of the matrix.
    sensors : list [str]
        The names of the sensors.
    n_sensors : int
        The number of sensors.
    n_elements : int
        The number of elements.
    n_values_per_element : int
        The number of values by element.
    elements_path : PathLike
        The path to the elements file.
    solution_paths : list [PathLike]
        The paths to the solutions.
    is_finalized : bool
        ``True`` if the solution is finalized.

    See Also
    --------
    shamo.solutions.ParametricForwardSolution
    """

    from shamo import EEGParametricForwardProblem, EEGForwardProblem, EEGForwardSolution

    PROBLEM_FACTORY = EEGParametricForwardProblem
    N_VALUES_PER_ELEMENT = 3
    SOLUTION_FACTORY = EEGForwardSolution
    SUB_PROBLEM_FACTORY = EEGForwardProblem

    def generate_surrogate_model(self, n_restarts_optimizer=0, n_jobs=None):
        """Generate the surrogate model.

        Parameters
        ----------
        n_restarts_optimizer : int, optional
            The number of trials for the optimizer. (The default is ``0``)
        n_jobs : int, optional
            The number of elements for which the regression is performed in parallel.
            ``1`` means one and ``None`` means all the cores are used. (The default is
            ``None``)

        Returns
        -------
        shamo.solutions.ParametricForwardSolution
            The current solution.
        """
        x, y = self._get_x_y()
        kernel = kernels.ConstantKernel() * kernels.Matern(
            length_scale=[1.0] * x.shape[1], nu=2.5
        )
        model = MultiOutputRegressor(
            GaussianProcessRegressor(
                kernel=kernel,
                n_restarts_optimizer=n_restarts_optimizer,
                normalize_y=True,
                random_state=0,
            ),
            n_jobs=n_jobs,
        )
        tmp = Path(self.path) / "tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        print(tmp)
        gen = (
            [i, x, y[:, i], kernel, tmp, n_restarts_optimizer]
            for i in range(y.shape[1])
        )
        if n_jobs == 1:
            paths = iter.starmap(self._fit_single, gen)
        else:
            with mp.Pool(n_jobs) as p:
                paths = p.starmap(self._fit_single, gen)
        model.estimators_ = [pickle.load(open(p, "rb")) for p in paths]
        surrogate_model_path = str(
            Path(self.path) / "{}_surrogate.bin".format(self.name)
        )
        pickle.dump(model, open(surrogate_model_path, "wb"))
        self["surrogate_model_path"] = get_relative_path(
            surrogate_model_path, self.path
        )

    @staticmethod
    def _fit_single(i, x, y, kernel, tmp_dir, n_restarts_optimizer=0):
        gp = GaussianProcessRegressor(
            kernel=kernel,
            n_restarts_optimizer=n_restarts_optimizer,
            normalize_y=True,
            random_state=0,
        ).fit(x, y)
        gp_path = Path(tmp_dir) / f"gp_{i:08d}.bin"
        pickle.dump(gp, open(gp_path, "wb"))
        return gp_path

    def _get_x_y(self):
        """Fetch the design set.

        Returns
        -------
        numpy.ndarray
            The values of the conductivities.
        numpy.ndarray
            The serialized leadfield matrices.
        """
        varying = [
            name
            for name, tissue in self.problem.electrical_conductivity.items()
            if tissue.value.name != "constant"
        ]
        self["varying"] = varying
        solutions = self.get_solutions()
        x = []
        y = []
        for solution in solutions:
            x.append(
                [
                    solution.problem.electrical_conductivity[tissue].value
                    for tissue in varying
                ]
            )
            y.append(solution.get_matrix(memory_map=True).reshape((-1,)))
        return np.array(x), np.array(y)

    def generate_matrix(self, **kwargs):
        """Generate a new matrix based on the surrogate model.

        Returns
        -------
        numpy.ndarray
            The generated matrix.
        """
        x = []
        for name in self["varying"]:
            value = kwargs.get(
                name, self.problem.electrical_conductivity[name].value.expected
            )
            x.append(value)
        model = self.get_surrogate_model()
        return model.predict([x]).reshape(self.shape)

    def generate_solution(self, name, parent_path, **kwargs):
        """Generate a solution based on the surrogate model.

        Parameters
        ----------
        name : str
            The name of the solution.
        parent_path : PathLike
            The path to the parent directory of the solution.

        Returns
        -------
        shamo.solutions.EEGForwardSolution
            The generated solution.

        Notes
        -----
        You can pass any named parameter corresponding to a varying parameter.
        """
        # Define the parameters used
        problem = self.SUB_PROBLEM_FACTORY()
        problem.add_regions_of_interest(self.problem.regions_of_interest)
        problem.add_markers(self.problem.markers)
        problem.set_reference(self.problem.reference)
        parameters = {}
        for name, property in self.problem.electrical_conductivity.items():
            if name in self["varying"]:
                parameters[name] = kwargs.get(
                    name, self.problem.electrical_conductivity[name].value.expected
                )
                problem.set_electrical_conductivity(
                    name,
                    parameters[name],
                    self.problem.electrical_conductivity[name].anisotropy,
                )
            else:
                problem.set_electrical_conductivity(
                    name,
                    self.problem.electrical_conductivity[name].value.value,
                    self.problem.electrical_conductivity[name].anisotropy,
                )
        # Compute the matrix
        matrix = self.generate_matrix(**parameters)
        # Generate the solution
        solution = self.SOLUTION_FACTORY(name, parent_path)
        solution.set_problem(problem)
        solution.set_model_path(self.model_path)
        solution.set_matrix(matrix)
        solution.set_elements_path(self.elements_path)
        solution.set_sensors(self.sensors)
        return solution
