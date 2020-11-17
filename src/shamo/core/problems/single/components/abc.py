"""Implement `CompABC` class."""
from abc import ABC, abstractmethod


class CompABC(dict, ABC):
    """A base class for any problem component.

    Components are the building bricks of all the problems.
    """

    def __init__(self, **kwargs):
        self.update(kwargs)

    @abstractmethod
    def check(self, name, **kwargs):
        """Check if the component is properly configured."""

    @abstractmethod
    def to_pro_param(self, **kwargs):
        """Return an object to be used as a parameter in the rendering of a PRO file."""

    @abstractmethod
    def to_py_param(self, **kwargs):
        """Return an object to be used as a parameter in the rendering of a PY file."""
