"""Implement `DistABC` class."""
from abc import ABC, abstractproperty

import chaospy as chaos


class DistABC(dict, ABC):
    """A base class for any probability distribution.

    Parameters
    ----------
    dist_type : str
        The type of the distribution.
    """

    TYPE_CONSTANT = "constant"
    TYPE_NORMAL = "normal"
    TYPE_TRUNC_NORMAL = "trunc_normal"
    TYPE_UNIFORM = "uniform"

    def __init__(self, dist_type, **kwargs):
        super().__init__({"dist_type": dist_type})

    @property
    def dist_type(self):
        """Return the type of the distribution.

        Returns
        -------
        str
            The type of the distribution.
        """
        return self["dist_type"]

    @abstractproperty
    def dist(self):
        """Return the actual distribution.

        Returns
        -------
        chaospy.Distribution
            The actual distribution.
        """

    @abstractproperty
    def uniform_dist(self):
        """Return a uniform distribution used for sampling.

        Returns
        -------
        chaospy.Uniform
            The uniform distribution.
        """

    @abstractproperty
    def salib_name(self):
        """Return the name of the distribution in SALib.

        Returns
        -------
        str
            The name of the distribution in SALib.
        """

    @abstractproperty
    def salib_bounds(self):
        """Return the bounds of the distribution in SALib.

        Returns
        -------
        list [float]
            The bounds of the distribution in SALib.
        """

    @property
    def expect(self):
        """Return the expected value of the distribution.

        Returns
        -------
        float
            The expected value of the distribution.
        """
        return float(chaos.E(self.dist))

    @staticmethod
    def load(dist_type, **kwargs):
        """Load a distribution from its dict representation.

        Returns
        -------
        DistABC
            The loaded distribution.
        """
        from .constant import DistConstant
        from .normal import DistNormal, DistTruncNormal
        from .uniform import DistUniform

        dist_types = {
            DistABC.TYPE_CONSTANT: DistConstant,
            DistABC.TYPE_NORMAL: DistNormal,
            DistABC.TYPE_TRUNC_NORMAL: DistTruncNormal,
            DistABC.TYPE_UNIFORM: DistUniform,
        }
        return dist_types[dist_type](**kwargs)
