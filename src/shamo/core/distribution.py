"""Implement the `Distribution` class.

This module implements the `Distribution` class and all its subclasses which
hold each the data for a specific distribution.
"""
import abc

import chaospy as chaos


class Distribution(dict, abc.ABC):
    """The base class for any distribution.

    Parameters
    ----------
    name : str
        The name of the distribution.

    Notes
    -----
    All the distribution should inherit from this class but, to be able to use
    them in other methods, they should correspond to distributions from
    `chaospy`.
    """

    def __init__(self, name):
        self["name"] = name

    @property
    def name(self):
        """Return the name of the distribution.

        Returns
        -------
        str
            The name of th distribution.
        """
        return self["name"]

    def expected(self):
        """Return the expected value corresponding to the distribution.

        Returns
        -------
        float
            The expected value.
        """
        return float(chaos.E(self.distribution))

    @abc.abstractproperty
    def distribution(self):
        """Return the actual distribution.

        Returns
        -------
        chaospy.distributions.baseclass.Dist
            The distribution.
        """

    @staticmethod
    def load(data):
        """Load a distribution from a dictionary.

        Parameters
        ----------
        data : dict [str, object]
            The dictionary containing the distribution information.

        Returns
        -------
        shamo.core.distribution.Distribution
            The loaded distribution.
        """
        name = data.get("name", "")
        if name == "constant":
            return ConstantDistribution(data.get("value"))
        elif name == "uniform":
            return UniformDistribution(data.get("minimum"), data.get("maximum"))
        elif name == "truncated_normal":
            return TruncatedNormalDistribution(
                data.get("minimum"),
                data.get("maximum"),
                data.get("sigma"),
                data.get("mu"),
            )


class ConstantDistribution(Distribution):
    """Define a constant value.

    Parameters
    ----------
    value : float
        The constant value.
    """

    def __init__(self, value):
        super().__init__("constant")
        self["value"] = float(value)

    @property
    def value(self):
        """Return the value.

        Returns
        -------
        float
            The value.
        """
        return self["value"]

    @property
    def expected(self):
        """Return the expected value corresponding to the distribution.

        Returns
        -------
        float
            The expected value.
        """
        return self["value"]

    @property
    def distribution(self):
        """Return ``None``."""
        return None


class UniformDistribution(Distribution):
    """Define a uniform distribution.

    Parameters
    ----------
    minimum : float
        The minimum value.
    maximum : float
        The maximum value.
    """

    def __init__(self, minimum, maximum):
        super().__init__("uniform")
        self["minimum"] = minimum
        self["maximum"] = maximum

    @property
    def minimum(self):
        """Return the minimum value.

        Returns
        -------
        float
            The minimum value.
        """
        return self["minimum"]

    @property
    def maximum(self):
        """Return the maximum value.

        Returns
        -------
        float
            The maximum value.
        """
        return self["maximum"]

    @property
    def distribution(self):
        """Return the actual distribution.

        Returns
        -------
        chaospy.distributions.collection.uniform.Uniform
            The distribution.
        """
        return chaos.Uniform(self.minimum, self.maximum)


class TruncatedNormalDistribution(Distribution):
    """Define a truncated normal distribution.

    Parameters
    ----------
    minimum : float
        The minimum value.
    maximum : float
        The maximum value.
    mu : float
        The mean value.
    sigma : float
        The standard deviation.
    """

    def __init__(self, minimum, maximum, mu, sigma):
        super().__init__("truncated_normal")
        self["minimum"] = minimum
        self["maximum"] = maximum
        self["mu"] = mu
        self["sigma"] = sigma

    @property
    def minimum(self):
        """Return the minimum value.

        Returns
        -------
        float
            The minimum value.
        """
        return self["minimum"]

    @property
    def maximum(self):
        """Return the maximum value.

        Returns
        -------
        float
            The maximum value.
        """
        return self["maximum"]

    @property
    def mu(self):
        """Return the mean value.

        Returns
        -------
        float
            The mean value.
        """
        return self["mu"]

    @property
    def sigma(self):
        """Return the standard deviation.

        Returns
        -------
        float
            The standard deviation.
        """
        return self["sigma"]

    @property
    def distribution(self):
        """Return the actual distribution.

        Returns
        -------
        chaospy.distributions.collection.trunc_normal.TruncNormal
            The distribution.
        """
        return chaos.TruncNormal(self.minimum, self.maximum, self.mu, self.sigma)
