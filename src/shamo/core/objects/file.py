"""Implement the `ObjFile` class."""
import json

from .abc import ObjABC


class ObjFile(ObjABC):
    """A base class for any savable/loadable object stored as a single JSON file.

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

    @property
    def path(self):
        """An alias for `json_path`.

        Returns
        -------
        pathlib.Path
            The path to the object JSON file.
        """
        return self.json_path

    @property
    def json_path(self):
        """Return the path to the object JSON file.

        Returns
        -------
        pathlib.Path
            The path to the object JSON file.
        """
        return self.parent_path / f"{self.name}.json"

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
        return json_path.stem, json_path.parent
