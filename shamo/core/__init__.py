"""API for `shamo.core`."""
from .objects import Object, FileObject, DirObject
from .problem import Problem
from .solution import Solution

__all__ = ["Object", "FileObject", "DirObject", "Problem", "Solution"]
