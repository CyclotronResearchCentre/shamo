"""Implement path methods."""
from pathlib import Path


def get_relative_path(path, relative_to):
    """Generate a relative path.

    Parameters
    ----------
    path : PathLike
        The path to edit.
    relative_to : PathLike
        The source point of the relative path.

    Returns
    -------
    str
        The relative path
    """
    origin = Path(relative_to).expanduser().resolve()
    destination = Path(path).expanduser().resolve()
    from_here = False
    relative_path = ""
    while not from_here:
        try:
            current_relative_path = str(destination.relative_to(origin))
            return relative_path + current_relative_path
        except ValueError:
            relative_path += "../"
            origin = origin.parent
