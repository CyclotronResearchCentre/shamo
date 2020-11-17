"""Implement `DistUniform` class."""
from .abc import DistABC

import chaospy as chaos


class DistUniform(DistABC):
    """A uniform distribution.

    Parameters
    ----------
    lower : float
        The lower bound of the distribution.
    upper : float
        The upper bound of the distribution.
    """

    def __init__(self, lower, upper):
        super().__init__("uniform")
        self.update({"lower": lower, "upper": upper})

    @property
    def lower(self):
        """Return the lower bound of the distribution.

        Returns
        -------
        float
            The lower bound of the distribution.
        """
        return self["lower"]

    @property
    def upper(self):
        """Return the upper bound of the distribution.

        Returns
        -------
        float
            The upper bound of the distribution.
        """
        return self["upper"]

    @property
    def dist(self):
        """Return the actual distribution.

        Returns
        -------
        chaospy.Uniform
            The actual distribution.
        """
        return chaos.Uniform(self.lower, self.upper)
