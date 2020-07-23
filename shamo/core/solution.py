"""Implement `Solution` class.

This module implements the `Solution` class which is the base for any solution.
"""
from pathlib import Path

from .objects import DirObject
from shamo.utils import none_callable, get_relative_path


class Solution(DirObject):
    """The base for any solution.

    Parameters
    ----------
    name : str
        The name of the solution.
    parent_path : PathLike
        The path to the parent directory of the solution.

    Other Parameters
    ----------------
    problem : dict [str, Any]
        The problem that result in this solution.
    model_path : PathLike
        The path to the model file.
    """

    PROBLEM_FACTORY = none_callable

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path)
        # Problem settings
        problem = kwargs.get("problem", None)
        if problem is not None:
            self["problem"] = self.PROBLEM_FACTORY(**problem)
        else:
            self["problem"] = problem
        # Model path
        model_path = kwargs.get("model_path", None)
        if model_path is not None:
            self["model_path"] = str(Path(model_path))
        else:
            self["model_path"] = None

    @property
    def problem(self):
        """Return the problem that result in this solution.

        Returns
        -------
        shamo.core.problem.Problem
            The problem that result in this solution.
        """
        return self["problem"]

    @property
    def model_path(self):
        """Return the path to the model file.

        Returns
        -------
        str
            The path to the model file.

        Raises
        ------
        FileNotFoundError
            If the model does not contain a model.
            If the FE model file does not exist.
        """
        # Check if the model file exists
        if self["model_path"] is None:
            raise FileNotFoundError("The solution does not contain a model.")
        path = Path(self.path) / self["model_path"]
        if not path.exists():
            raise FileNotFoundError(("The specified model file no longer " "exists."))
        return str(path)

    def set_problem(self, problem):
        """Set the problem that result in this solution.

        Parameters
        ----------
        problem : shamo.core.problem.Problem
            The problem that result in this solution.

        Returns
        -------
        shamo.core.solution.Solution
            The solution.
        """
        self["problem"] = problem
        return self

    def set_model_path(self, model_path):
        """Set the path to the model used to generate the solution.

        Parameters
        ----------
        model_path : PathLike
            The path to the model used to generate the solution.

        Returns
        -------
        shamo.core.solution.Solution
            The solution.
        """
        self["model_path"] = get_relative_path(model_path, self.path)
        return self

    def set_model(self, model):
        """Set the model used to generate the solution.

        Parameters
        ----------
        model : shamo.model.fe_model.FEModel
            The model used to generate the solution.

        Returns
        -------
        shamo.core.solution.Solution
            The solution.
        """
        self["model_path"] = get_relative_path(model.json_path, self.path)
        return self
