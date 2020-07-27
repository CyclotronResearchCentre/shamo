"""API for `shamo.utils`."""
from .template_file import TemplateFile
from .path import get_relative_path
from .mesh import (
    get_elements_coordinates,
    get_tissue_elements,
    get_equally_spaced_elements,
)


def none_callable(*args, **kwargs):
    """Return `None`."""
    return None


__all__ = [
    "none_callable",
    "TemplateFile",
    "get_relative_path",
    "get_elements_coordinates",
    "get_tissue_elements",
    "get_equally_spaced_elements",
]
