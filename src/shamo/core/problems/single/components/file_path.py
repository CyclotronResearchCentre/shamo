"""Implement `CompFilePath` class."""
import logging
from pathlib import Path

from .abc import CompABC

logger = logging.getLogger(__name__)


class CompFilePath(CompABC):
    """Store information about a path.

    Other Parameters
    ----------------
    path : pathlib.Path
        The path to the file.
    """

    def __init__(self, **kwargs):
        super().__init__(path=kwargs.get("path", None))

    @property
    def use_path(self):
        """Return ``True`` if a path is set.

        Returns
        -------
        bool
            ``True`` if a path is set, ``False`` otherwise.
        """
        return self["path"] is not None

    @property
    def path(self):
        """Return the path.

        Returns
        -------
        pathlib.Path
            The path.
        """
        return self["path"]

    def set(self, path):
        """Set the path.

        Parameters
        ----------
        path : str, byte or os.PathLike
            The path.
        """
        self["path"] = Path(path)

    def check(self, name, **kwargs):
        """Check if the path is properly set."""
        logger.info(f"Checking file path for '{name}'.")
        if self.use_path:
            if not self["path"].exists():
                raise FileNotFoundError("Argument 'path' does not exist.")

    def to_pro_param(self, **kwargs):
        """Return ``None``."""
        return None

    def to_py_param(self, **kwargs):
        """Return the path."""
        return str(self.path)
