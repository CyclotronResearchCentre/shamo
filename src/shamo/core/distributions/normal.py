"""Implement `DistNormal` and `DistTruncNormal` classes."""
from .abc import DistABC

import chaospy as chaos


class DistNormal(DistABC):
    """A normal distribution.

    Parameters
    ----------
    mu : float
        The mean of the distribution.
    sigma : float
        The standard deviation of the distribution.
    """

    def __init__(self, mu, sigma):
        super().__init__(self.TYPE_NORMAL)
        self.update({"mu": mu, "sigma": sigma})

    @property
    def mu(self):
        """Return the mean of the distribution.

        mu : float
            The mean of the distribution.
        """
        return self["mu"]

    @property
    def sigma(self):
        """Return the standard deviation of the distribution.

        sigma : float
            The standard deviation of the distribution.
        """
        return self["sigma"]

    @property
    def dist(self):
        """Return the actual distribution.

        Returns
        -------
        chaospy.Normal
            The actual distribution.
        """
        return chaos.Normal(mu=self.mu, sigma=self.sigma)

    @property
    def uniform_dist(self):
        """Return a uniform distribution used for sampling.

        Returns
        -------
        chaospy.Uniform
            The uniform distribution.
        """
        return chaos.Uniform(
            lower=self.mu - 3 * self.sigma, upper=self.mu + 3 * self.sigma
        )

    @property
    def salib_name(self):
        """Return the name of the distribution in SALib.

        Returns
        -------
        str
            The name of the distribution in SALib.
        """
        return "norm"

    @property
    def salib_bounds(self):
        """Return the bounds of the distribution in SALib.

        Returns
        -------
        list [float]
            The bounds of the distribution in SALib.
        """
        return [self.mu, self.sigma]


class DistTruncNormal(DistABC):
    """A truncated normal distribution.

    Parameters
    ----------
    mu : float
        The mean of the distribution.
    sigma : float
        The standard deviation of the distribution.
    lower : float
        The lower bound of the distribution.
    upper : float
        The upper bound of the distribution.
    """

    def __init__(self, mu, sigma, lower, upper):
        super().__init__(self.TYPE_TRUNC_NORMAL)
        self.update({"mu": mu, "sigma": sigma, "lower": lower, "upper": upper})

    @property
    def mu(self):
        """Return the mean of the distribution.

        mu : float
            The mean of the distribution.
        """
        return self["mu"]

    @property
    def sigma(self):
        """Return the standard deviation of the distribution.

        sigma : float
            The standard deviation of the distribution.
        """
        return self["sigma"]

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
        chaospy.TruncNormal
            The actual distribution.
        """
        return chaos.Normal(
            mu=self.mu, sigma=self.sigma, lower=self.lower, upper=self.upper
        )

    @property
    def uniform_dist(self):
        """Return a uniform distribution used for sampling.

        Returns
        -------
        chaospy.Uniform
            The uniform distribution.
        """
        return chaos.Uniform(lower=self.lower, upper=self.upper)

    @property
    def salib_name(self):
        """Return the name of the distribution in SALib.

        Returns
        -------
        str
            The name of the distribution in SALib.
        """
        return "truncnorm"

    @property
    def salib_bounds(self):
        """Return the bounds of the distribution in SALib.

        Returns
        -------
        list [float]
            The bounds of the distribution in SALib.
        """
        return [self.lower, self.upper, self.mu, self.sigma]
