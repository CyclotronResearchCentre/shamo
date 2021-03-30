"""Implement `DistConstant` class."""
from .abc import DistABC


class DistConstant(DistABC):
    """A constant value for a random parameter.

    When dealing with parametric problems, some parameters are supposed random. If one
    of them is known, it must be modelled by this class.

    Parameters
    ----------
    val : float
        The constant value.
    """

    def __init__(self, val):
        super().__init__(self.TYPE_CONSTANT)
        self.update({"val": val})

    @property
    def val(self):
        """Return the constant value.

        Returns
        -------
        float
            The constant value.
        """
        return self["val"]

    @property
    def expect(self):
        """Return the constant value.

        Returns
        -------
        float
            The constant value.
        """
        return self.val

    @property
    def dist(self):
        """Return ``None``."""
        return None

    @property
    def uniform_dist(self):
        """Return ``None``."""
        return None

    @property
    def salib_name(self):
        """Return the name of the distribution in SALib.

        Returns
        -------
        str
            The name of the distribution in SALib.
        """
        return ""

    @property
    def salib_bounds(self):
        """Return the bounds of the distribution in SALib.

        Returns
        -------
        list [float]
            The bounds of the distribution in SALib.
        """
        return []
