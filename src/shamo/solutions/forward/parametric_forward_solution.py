"""Implement the `ParametricForwardSolution` class.

This module implements the `ParametricForwardSolution` class which is the base
for any parametric forward solution.
"""
import abc
from pathlib import Path
import pickle
import re
import shutil

from shamo.solutions import CommonForwardSolution
from shamo.utils import none_callable


class ParametricForwardSolution(CommonForwardSolution):
    """The base for any parametric forward problem solution.

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
    shamo.solutions.forward.common_forward_solution.CommonForwardSolution
    """

    SOLUTION_FACTORY = none_callable

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        # Quadrature
        self["quadrature"] = kwargs.get("quadrature", {})
        # Sub-solutions paths
        self["solution_paths"] = [
            str(Path(path)) for path in kwargs.get("solution_paths", [])
        ]
        # Is finalized
        self["is_finalized"] = kwargs.get("is_finalized", False)
        # Surrogate model path
        surrogate_model_path = kwargs.get("surrogate_model_path", None)
        if surrogate_model_path is not None:
            self["surrogate_model_path"] = str(Path(surrogate_model_path))
        else:
            self["surrogate_model_path"] = None
        self._surrogate_model = None

    @property
    def quadrature(self):
        """Return the quadrature settings.

        Returns
        -------
        dict [str, Any]
            The quadrature settings.
        """
        return self["quadrature"]

    @property
    def solution_paths(self):
        """Return the paths to the solutions.

        Returns
        -------
        list [str]
            The paths to the solutions.
        """
        return [str(Path(self.path) / path) for path in self["solution_paths"]]

    @property
    def is_finalized(self):
        """Return wether the solution is finalized or not.

        Returns
        -------
        bool
            ``True`` if the solution is finalized, ``False`` otherwise.
        """
        return self["is_finalized"]

    @property
    def surrogate_model_path(self):
        """Return the path to model file.

        Returns
        -------
        str
            The path to model file.

        Raises
        ------
        FileNotFoundError
            If the solution does not contain a model file.
            If the model file does not exist.
        """
        # Check if the matrix file exists
        if self["surrogate_model_path"] is None:
            raise FileNotFoundError("The model does not contain a model.")
        path = Path(self.path) / self["surrogate_model_path"]
        if not path.exists():
            raise FileNotFoundError(("The specified model file no longer " "exists."))
        return str(path)

    def set_quadrature(self, order, rule, sparse):
        """Set the quadrature settings.

        Parameters
        ----------
        order : int
            The order of the quadrature.
        rule : str
            The quadrature rule.
        sparse : bool
            If set to ``True``, the quadrature is sparse.

        Returns
        -------
        shamo.solutions.ParametricForwardSolution
            The current solution.
        """
        self["quadrature"] = {"order": order, "rule": rule, "sparse": sparse}
        return self

    def get_solutions(self):
        """Return the solutions.

        Returns
        -------
        list [shamo.core.solution.Solution]
            The solutions.
        """
        return [self.SOLUTION_FACTORY.load(path) for path in self.solution_paths]

    def get_surrogate_model(self):
        """Load the surrogate model.

        Returns
        -------
        object
            The surrogate model.
        """
        # Make sure to only load it once
        if self._surrogate_model is None:
            self._surrogate_model = pickle.load(open(self.surrogate_model_path, "rb"))
        return self._surrogate_model

    def finalize(self, clean=True):
        """Finalize the generation of the parametric solution.

        Parameters
        ----------
        clean : bool, optional
            If set to ``True``, all the temporary files created during the
            generation are removed. (The default is ``True``)

        Returns
        -------
        shamo.solutions.ParametricForwardSolution
            The current solution.

        Raises
        ------
        RuntimeError
            If the solution is not finalized and no sub-solution was found.
        """
        if self.is_finalized:
            return self
        # Check if can be finalized
        sub_paths = []
        pattern = re.compile(r"sol_\d{8}")
        for entry in Path(self.path).iterdir():
            name = entry.name
            if entry.is_dir() and pattern.match(name):
                sub_paths.append(str(Path(name) / "{}.json".format(name)))
        if len(sub_paths) == 0:
            raise RuntimeError("No sub-solution found.")
        self["solution_paths"] = sorted(sub_paths)
        # Remove all `.py` files
        if clean:
            for entry in Path(self.path).iterdir():
                if entry.suffix == ".py":
                    entry.unlink()
        # Set common data
        solutions = self.get_solutions()
        self["shape"] = solutions[0].shape
        self["sensors"] = solutions[0].sensors
        # Remove duplicated elements files
        elements_path = "{}_elements.npz".format(self.name)
        shutil.copy(solutions[0].elements_path, str(Path(self.path) / elements_path))
        self["elements_path"] = elements_path
        for solution in solutions:
            Path(solution.elements_path).unlink()
            solution["elements_path"] = str(Path("..") / elements_path)
            solution.save()
        # Generate the surrogate model
        self.generate_surrogate_model()
        self["is_finalized"] = True
        self.save()
        return self

    @abc.abstractmethod
    def generate_surrogate_model(self):
        """Generate the surrogate model.

        Returns
        -------
        shamo.solutions.ParametricForwardSolution
            The current solution.
        """

    @abc.abstractmethod
    def generate_matrix(self, **kwargs):
        """Generate a new matrix based on the surrogate model.

        Returns
        -------
        numpy.ndarray
            The generated matrix.

        Notes
        -----
        You can pass any named parameter corresponding to a varying parameter.
        """

    @abc.abstractmethod
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
        shamo.solutions.ForwardSolution
            The generated solution.

        Notes
        -----
        You can pass any named parameter corresponding to a varying parameter.
        """
