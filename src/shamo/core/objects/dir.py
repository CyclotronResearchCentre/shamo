"""Implement the `ObjDir` class."""
import json
from pathlib import Path

from .abc import ObjABC
from shamo.utils.path import get_relative_path as get_rel_path


class ObjDir(ObjABC):
    """A base class for any savable/loadable object stored as a directory.

    Parameters
    ----------
    name : str
        The name of the object.
    parent_path : str, byte or os.PathLike
        The path to the parent directory of the object.

    See Also
    --------
    shamo.core.ObjABC
    """

    def __init__(self, name, parent_path):
        super().__init__(name, parent_path)
        self.path.mkdir(parents=True, exist_ok=True)

    @property
    def path(self):
        """Return the path to the object directory.

        Returns
        -------
        pathlib.Path
            The path to the object directory.
        """
        return self.parent_path / self.name

    @property
    def json_path(self):
        """Return the path to the object JSON file.

        Returns
        -------
        pathlib.Path
            The path to the object JSON file.
        """
        return self.path / f"{self.name}.json"

    @classmethod
    def _split_json_path(cls, json_path):
        """Return the path and the name of the object from the path of the JSON file.

        Parameters
        ----------
        json_path : pathlib.Path
            The path to the JSON file containing the object data.

        Returns
        -------
        str
            The name of the object.
        pathlib.Path
            The path to the parent directory of the object.
        """
        return json_path.stem, json_path.parents[1]

    def get_relative_path(self, path):
        """Return the relative path from the object to a file or directory.

        Parameters
        ----------
        path : str, byte or os.PathLike
            The path to the file or directory to compute the relative path for.

        Returns
        -------
        pathlib.Path
            The relative path to the file or directory.
        """
        return get_rel_path(self.path, path)
