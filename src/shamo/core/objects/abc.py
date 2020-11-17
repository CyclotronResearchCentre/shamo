"""Implement the `ObjABC` class."""
from abc import ABC, abstractclassmethod, abstractproperty
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ObjABC(dict, ABC):
    """A base class for any savable/loadable object.

    All the main object can be saved to/loaded from human readable JSON files to make it
    easily compatible with BIDS standars and simplify interactions with other scripts.

    Parameters
    ----------
    name : str
        The name of the object.
    parent_path : str, byte or os.PathLike
        The path to the parent directory of the object.

    Raises
    ------
    TypeError
        If argument `name` is not a `str`.
        If argument `parent_path` is not a `str`, `byte` or `os.PathLike`.
    """

    def __init__(self, name, parent_path):
        super().__init__()
        if not isinstance(name, str):
            raise TypeError(f"Argument 'name' expects type str, not {type(name)}.")
        self._name = name
        self._parent_path = Path(parent_path)

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
    def parent_path(self):
        """Return the path to the parent directory of the object.

        Returns
        -------
        pathlib.Path
            The path to the parent directory of the object.
        """
        return self._parent_path

    @abstractproperty
    def path(self):
        """Return the path to the object.

        Returns
        -------
        pathlib.Path
            The path to the object.
        """

    @abstractproperty
    def json_path(self):
        """Return the path to the object JSON file.

        Returns
        -------
        pathlib.Path
            The path to the object JSON file.
        """
        pass

    def save(self, exist_ok=True):
        """Save the object to a JSON file.

        Parameters
        ----------
        exist_ok : bool, optional
            If set to ``True``, any already existing object is overriden. Otherwise, if
            the object already exists, a `FileExistsError`. The default is ``True``.

        Raises
        ------
        FileExistsError
            If `exist_ok` is set to ``False`` and the object already exists.
        TypeError
            If any of the keys/values to be stored is not a `str`, `int`, `float`,
            `bool` or ``None``.
        """
        self.parent_path.mkdir(parents=True, exist_ok=True)
        if not exist_ok and self.json_path.exists():
            raise FileExistsError(
                (
                    f"File '{str(self.json_path)}' already exists. "
                    "If you want to override it, set argument 'exist_ok' to True."
                )
            )
        with open(self.json_path, "w") as f:
            json.dump(self, f, indent=4, sort_keys=True)

    @abstractclassmethod
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
        pass

    @classmethod
    def load(cls, json_path):
        """Load an object from a JSON file.

        Parameters
        ----------
        json_path : str, byte or os.PathLike
            The path to the JSON file containing the object data.

        Raises
        ------
        TypeError
            If argument `json_path` is not a `str`, `byte` or `os.PathLike`.

        """
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"File '{str(json_path)}' does not exist.")
        if not json_path.suffix == ".json":
            raise ValueError(f"Argument 'json_path' must end with '.json'.")
        with open(json_path, "r") as f:
            data = json.load(f)
        return cls(*cls._split_json_path(json_path), **data)
