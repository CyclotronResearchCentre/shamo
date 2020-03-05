"""Implement `Problem` class.

This module implements the `Problem` class which is the base for any problem.
"""
import abc


class Problem(dict):
    """The base for any problem."""

    @abc.abstractmethod
    def check_settings(self, model, **kwargs):
        """Check wether the current settings fit to the model.

        Parameters
        ----------
        model : shamo.core.FileObject
            The model to check the settings for.
        """

    @abc.abstractmethod
    def solve(self, name, parent_path, model, **kwargs):
        """Solve the problem.

        Parameters
        ----------
        name : str
            The name of the solution.
        parent_path : PathLike
            The path to the parent directory of the solution.
        model : shamo.core.FileObject
            The model to solve the problem on.

        Returns
        -------
        shamo.core.Solution
            The solution of the problem for the specified model.
        """
