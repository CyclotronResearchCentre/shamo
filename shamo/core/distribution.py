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

    Attributes
    ----------
    name
    expected
    distribution
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
        chaospy.Distribution
            The distribution.
        """

    @staticmethod
    def load(data):
        """Load a distribution from a dictionary.

        Parameters
        ----------
        data : dict[str: object]
            The dictionary containing the distribution information.

        Returns
        -------
        shamo.Distribution
            The loaded distribution.
        """
        name = data.get("name", "")
        if name == "constant":
            return ConstantDistribution(data.get("value"))
        elif name == "uniform":
            return UniformDistribution(
                data.get("minimum"), data.get("maximum"))


class ConstantDistribution(Distribution):
    """Define a constant value.

    Parameters
    ----------
    value : float
        The constant value.

    Attributes
    ----------
    name
    value
    expected
    distribution
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
            The value
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
        """Return `None`."""
        return None


class UniformDistribution(Distribution):
    """Define a uniform distribution.

    Parameters
    ----------
    minimum : float
        The minimum value.
    maximum : float
        The maximum value.

    Attributes
    ----------
    name
    minimum
    maximum
    expected
    distribution
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
            The minimum value
        """
        return self["minimum"]

    @property
    def maximum(self):
        """Return the maximum value.

        Returns
        -------
        float
            The maximum value
        """
        return self["maximum"]

    @property
    def distribution(self):
        """Return the actual distribution.

        Returns
        -------
        chaospy.Uniform
            The distribution.
        """
        return chaos.Uniform(self.minimum, self.maximum)
