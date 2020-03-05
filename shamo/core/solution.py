"""Implement `Solution` class.

This module implements the `Solution` class which is the base for any solution.
"""
from .objects import DirObject

from shamo.utils import none_callable


class Solution(DirObject):
    """The base for any solution.

    Parameters
    ----------
    name : str
        The name of the solution.
    parent_path : PathLike
        The path to the parent directory of the solution.

    Attributes
    ----------
    problem

    Other Parameters
    ----------------
    problem : dict[str: Any]
        The problem that result in this solution.
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

    @property
    def problem(self):
        """Return the problem that result in this solution.

        Returns
        -------
        shamo.core.Problem
            The problem that result in this solution.
        """
        return self["problem_settings"]

    def set_problem(self, problem):
        """Set the problem that result in this solution.

        Parameters
        ----------
        problem : shamo.core.Problem
            The problem that result in this solution.

        Returns
        -------
        shamo.core.Solution
            The solution.
        """
        self["problem"] = problem
        return self
