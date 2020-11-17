"""Implement the `ProbABC` class."""
from abc import ABC, abstractmethod


class ProbABC(dict, ABC):
    """A base class for any problem.

    All the main processes are defined as problem/solution pairs. The problem defines
    the parameters and builds the solution.
    """

    @abstractmethod
    def _check_components(self, **kwargs):
        """Check if all the components are properly set."""

    @abstractmethod
    def _prepare_py_file_params(self, **kwargs):
        """Return a dict filled with all the required parameters to generate a PY file.

        Returns
        -------
        dict [str, Any]
            The dict filled with all the required parameters.
        """

    @abstractmethod
    def solve(self, name, parent_path, **kwargs):
        """Solve the problem and build the solution object.

        Parameters
        ----------
        name : str
            The name of the solution.
        parent_path : str, byte or os.PathLike
            The path to the parent directory of the solution.

        Returns
        -------
        shamo.core.objects.ObjDir
            The solution.
        """
