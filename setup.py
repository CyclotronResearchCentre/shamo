"""Setup script for ``shamo``."""
from pathlib import Path
import re
import setuptools
from typing import Text


def get_version() -> Text:
    """Return the current version of the package extracted from ``CHANGELOG.md``.

    Returns
    -------
    Text
        The current version of the package.
    """
    with open(Path("CHANGELOG.md"), "r") as file:
        changelog = file.read()
    try:
        version = next(
            re.finditer(r"(?<=(## \[))[0-9a-z\.\-]*(?=\])", changelog)
        ).group(0)
    except StopIteration:
        version = "0.0.0"
    return version


if __name__ == "__main__":
    setuptools.setup(version=get_version())
