"""Implement `SolParamABC` class."""
from abc import abstractproperty, abstractmethod
from pathlib import Path
import re

from shamo.core.objects import ObjDir


class SolParamABC(ObjDir):
    """Store information about the solution of a parametric problem.

    Parameters
    ----------
    name : str
        The name of the solution.
    parent_path : str, byte or os.PathLike
        The path to the parent directory of the solution.

    Other Parameters
    ----------------
    sub_json_paths : list [str]
        The relative paths to the sub-solutions.
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path)
        self.update(
            {"sub_json_paths": [str(Path(p)) for p in kwargs.get("sub_json_paths", [])]}
        )
        self.sub_sols = self.get_sub_sols()

    @abstractproperty
    def sub_class(self):
        """Return the class of the sub-solutions.

        Returns
        -------
        shamo.core.objects.ObjDir
            The class of the sub-solutions.
        """

    @property
    def sub_json_paths(self):
        """Return the paths to the sub-solutions JSON files.

        Returns
        -------
        pathlib.Path
            The paths to the sub-solutions JSON files.
        """
        return [self.path / p for p in self["sub_json_paths"]]

    @abstractmethod
    def finalize(self, **kwargs):
        """Finalize the solution."""

    def _get_sub_json_paths(self):
        """Get the JSON paths of the sub-solutions."""
        self["sub_json_paths"] = self.get_sub_file(".json")

    def get_sub_sols(self):
        """Return the sub-solutions.

        Returns
        -------
        list [shamo.core.objects.ObjDir]
            The sub-solutions.
        """
        return [self.sub_class.load(p) for p in self.sub_json_paths]

    def get_sub_file(self, suffix):
        """Return the relative paths to the same file in all the sub-solutions.

        Returns
        -------
        list [str]
            The relative paths to the same file in all the sub-solutions.
        """
        return sorted(
            [
                str(p.relative_to(self.path) / f"{p.name}{suffix}")
                for p in self.path.iterdir()
                if p.is_dir and re.match(r"^.+_\d{8}$", p.name)
            ]
        )

    @abstractmethod
    def get_params(self):
        """Return the random parameters of the solution.

        Returns
        -------
        list [ list [str, Any]]
        """

    @abstractmethod
    def get_x(self, sub_sol):
        """Return the value of the random parameters in the sub solution.

        Parameters
        ----------
        sub_sol : shamo.core.solutions.SolABC
        """
