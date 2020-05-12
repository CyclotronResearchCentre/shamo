"""Implement the `Object`, `FileObject` and `DirObject` classes.

Those classes are the base for any object in `shamo` that needs to be saved to
and loaded from disk.
"""
import abc
import json
from pathlib import Path


class Object(dict, abc.ABC):
    """The abstract base class for any object in ``shamo``.

    Parameters
    ----------
    name : str
        The name of the object.
    parent_path : PathLike
        The path to the parent directory of the object on disk.
    """

    def __init__(self, name, parent_path):
        super().__init__()
        self._name = name
        self._parent_path = str(Path(parent_path).expanduser().absolute())

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
        """Return the path to the parent directory of the object on disk.

        Returns
        -------
        str
            The path to the parent directory of the object on disk.
        """
        return self._parent_path

    @abc.abstractproperty
    def path(self):
        """Return the path to the object on disk.

        Returns
        -------
        str
            The path to the object on disk.
        """

    @abc.abstractproperty
    def json_path(self):
        """Return the path to the ``.json`` file representing the object.

        Returns
        -------
        str
            The path to the ``.json`` file representing the object.
        """

    @abc.abstractmethod
    def save(self, parents=True, exist_ok=True):
        """Save the object.

        Parameters
        ----------
        parents : bool, optional
            If set to ``True``, the missing directories in the path are
            created. Otherwise, a missing parent raise ``FileNotFoundError``.
            (The default is ``True``)
        exist_ok : bool, optional
            If set to ``True``, override any existing file. Otherwise, if any
            existing file is found, raise ``FileExistsError``.
            (The default is ``True``)

        Raises
        ------
        FileNotFoundError
            If ``parents`` is set to ``False`` and a missing parent is found.
        FileExistsError
            If ``exist_ok`` is set to ``False`` and the object already exists.
        """

    @abc.abstractclassmethod
    def load(cls, json_path):
        """Load an object from a ``.json`` file.

        Parameters
        ----------
        json_path : PathLike
            The path to the ``.json`` file representing  the object.

        Returns
        -------
        Object
            The loaded object.

        Raises
        ------
        FileNotFoundError
            If the ``.json`` file does not exist.
        """


class FileObject(Object):
    """The base class for any single file object in ``shamo``.

    Parameters
    ----------
    name : str
        The name of the object.
    parent_path : PathLike
        The path to the parent directory of the object on disk.
    """

    def __init__(self, name, parent_path):
        super().__init__(name, parent_path)

    @property
    def path(self):
        """Return the path to the object on disk.

        Returns
        -------
        str
            The path to the object on disk.

        Notes
        -----
        For ``FileObject``, it returns the same path as ``json_path()``.
        """
        return self.json_path

    @property
    def json_path(self):
        """Return the path to the ``.json`` file representing the object.

        Returns
        -------
        str
            The path to the ``.json`` file representing the object.
        """
        return str(Path(self.parent_path) / "{}.json".format(self.name))

    def save(self, parents=True, exist_ok=True):
        """Save the object ``.json`` file.

        Parameters
        ----------
        parents : bool, optional
            If set to ``True``, the missing directories in the path are
            created. Otherwise, a missing parent raise ``FileNotFoundError``.
            (The default is ``True``)
        exist_ok : bool, optional
            If set to ``True``, override any existing file. Otherwise, if any
            existing file is found, raise ``FileExistsError``.
            (The default is ``True``)

        Raises
        ------
        FileNotFoundError
            If ``parents`` is set to ``False`` and a missing parent is found.
        FileExistsError
            If ``exist_ok`` is set to ``False`` and the object already exists.
        """
        # Make sure the parent directory exists
        parent_path = Path(self.parent_path)
        parent_path.mkdir(parents=parents, exist_ok=True)
        # Check if the file already exists
        json_path = Path(self.json_path)
        if not exist_ok and json_path.exists():
            raise FileExistsError("The object already exists.")
        # Save the object
        with open(str(json_path), "w") as json_file:
            json.dump(self, json_file, indent=4)

    @classmethod
    def load(cls, json_path):
        """Load an object from a ``.json`` file.

        Parameters
        ----------
        json_path : PathLike
            The path to the ``.json`` file representing  the object.

        Returns
        -------
        Object
            The loaded object.

        Raises
        ------
        FileNotFoundError
            If the ``.json`` file does not exist.
        """
        # Check if the file exists
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError("The object does not exist.")
        # Load the object
        with open(str(json_path), "r") as json_file:
            data = json.load(json_file)
        return cls(json_path.stem, json_path.parent, **data)


class DirObject(Object):
    """The base class for any directory object in ``shamo``.

    Parameters
    ----------
    name : str
        The name of the object.
    parent_path : PathLike
        The path to the parent directory of the object on disk.
    """

    def __init__(self, name, parent_path):
        super().__init__(name, parent_path)
        path = Path(self.parent_path) / name
        path.mkdir(parents=True, exist_ok=True)

    @property
    def path(self):
        """Return the path to the object on disk.

        Returns
        -------
        str
            The path to the directory of the object on disk.
        """
        return str(Path(self.parent_path) / self.name)

    @property
    def json_path(self):
        """Return the path to the ``.json`` file representing the object.

        Returns
        -------
        str
            The path to the ``.json`` file representing the object.
        """
        return str(Path(self.path) / "{}.json".format(self.name))

    def save(self, parents=True, exist_ok=True):
        """Save the object ``.json`` file in a new directory.

        Parameters
        ----------
        parents : bool, optional
            If set to ``True``, the missing directories in the path are
            created. Otherwise, a missing parent raise ``FileNotFoundError``.
            (The default is ``True``)
        exist_ok : bool, optional
            If set to ``True``, override any existing file. Otherwise, if any
            existing file is found, raise ``FileExistsError``.
            (The default is ``True``)

        Raises
        ------
        FileNotFoundError
            If ``parents`` is set to ``False`` and a missing parent is found.
        FileExistsError
            If ``exist_ok`` is set to ``False`` and the object already exists.
        """
        # Create the directory
        path = Path(self.path)
        path.mkdir(parents=parents, exist_ok=exist_ok)
        # Save the object
        with open(self.json_path, "w") as json_file:
            json.dump(self, json_file, indent=4)

    @classmethod
    def load(cls, json_path):
        """Load an object from a ``.json`` file.

        Parameters
        ----------
        json_path : PathLike
            The path to the ``.json`` file representing  the object.

        Returns
        -------
        Object
            The loaded object.

        Raises
        ------
        FileNotFoundError
            If the ``.json`` file does not exist.
        """
        # Check if the file exists
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError("The object does not exist.")
        # Load the object
        with open(str(json_path), "r") as json_file:
            data = json.load(json_file)
        return cls(json_path.stem, json_path.parents[1], **data)
