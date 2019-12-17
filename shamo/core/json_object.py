"""Implement the `JSONObject` class.

This module implements the `JSONObject` class which is the base class of any
savable/loadable object in `shamo`.
"""
from __future__ import annotations
import json
from pathlib import Path


class JSONObject(dict):
    """Short summary.

    Parameters
    ----------
    name : str
        The name given to the object.
    parent_path : str
        The path to the parent directory of the object.
    parents : bool
        If set to `True`, any missing level in the tree is created. (The
        default is `True`).
    exist_ok : bool
        If set to `True`, no exception is raised if the directory already
        exists. (The default is `True`).

    Attributes
    ----------
    path
    json_path
    """

    def __init__(self, name: str, parent_path: str, parents: bool = True,
                 exist_ok: bool = True, **kwargs) -> None:
        super().__init__()
        object_path = Path(parent_path) / name
        object_path.mkdir(parents=parents, exist_ok=exist_ok)
        self._name = name
        self._path = object_path
        self._json_path = object_path / "{}.json".format(name)

    @property
    def name(self):
        """Return the name of the object.

        Returns
        -------
        str
            The name of the object.
        """
        return self._name

    @property
    def path(self) -> str:
        """Return the path to the directory of the object.

        Returns
        -------
        str
            The path to the directory of the object.
        """
        return str(self._path)

    @property
    def json_path(self) -> str:
        """Return the path to the `.json` file of the object.

        Returns
        -------
        str
            The path to the `.json` file of the object.
        """
        return str(self._json_path)

    def save(self) -> None:
        """Save the data of the object in a `.json` file."""
        with open(self.json_path, "w") as json_file:
            json.dump(self, json_file)

    @classmethod
    def load(cls, path: str) -> JSONObject:
        """Load a `JSONObject` from a `.json` file.

        Parameters
        ----------
        path : str
            The path to the `.json` file.

        Returns
        -------
        JSONObject
            The loaded `JSONObject`.
        """
        json_path = Path(path)
        with open(json_path, "r") as json_file:
            data = json.load(json_file)
        return cls(json_path.stem, str(json_path.parents[1]), **data)
