"""API for `shamo.core.objects`."""
from .abc import ObjABC
from .dir import ObjDir
from .file import ObjFile

__all__ = ["ObjABC", "ObjDir", "ObjFile"]
