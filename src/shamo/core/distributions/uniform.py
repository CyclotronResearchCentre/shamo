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
        super().__init__(self.TYPE_UNIFORM)
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

    @property
    def uniform_dist(self):
        """Return a uniform distribution used for sampling.

        Returns
        -------
        chaospy.Uniform
            The uniform distribution.
        """
        return self.dist

    @property
    def salib_name(self):
        """Return the name of the distribution in SALib.

        Returns
        -------
        str
            The name of the distribution in SALib.
        """
        return "unif"

    @property
    def salib_bounds(self):
        """Return the bounds of the distribution in SALib.

        Returns
        -------
        list [float]
            The bounds of the distribution in SALib.
        """
        return [self.lower, self.upper]
