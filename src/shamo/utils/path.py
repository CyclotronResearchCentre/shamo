"""API for `shamo.utils.path`."""
from pathlib import Path


def get_relative_path(ref, path):
    """Return the relative path from the reference to a file or directory.

    Parameters
    ----------
    ref : str, byte or os.PathLike
        The path to the reference file or directory.
    path : str, byte or os.PathLike
        The path to the file or directory to compute the relative path for.

    Returns
    -------
    pathlib.Path
        The relative path to the file or directory.
    """
    ref = Path(ref).expanduser().resolve()
    path = Path(path).expanduser().resolve()
    here = False
    rel_path = ""
    while not here:
        try:
            current = str(path.relative_to(ref))
            return Path(rel_path + current)
        except ValueError:
            rel_path += "../"
            ref = ref.parent
