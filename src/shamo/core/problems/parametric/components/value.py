"""Implement the `CompParamValue` class."""
import logging

from shamo.core.problems.single import CompABC
from shamo import DistABC

logger = logging.getLogger(__name__)


class CompParamValue(CompABC):
    """Store information about a random value.

    Other Parameters
    ----------------
    val : shamo.DistABC
        The random value.
    """

    def __init__(self, **kwargs):
        self["val"] = kwargs.get("val", None)

    @property
    def val(self):
        """Return the random value.

        Returns
        -------
        shamo.DistABC
            The random value.
        """
        return self["val"]

    def check(self, name, **kwargs):
        """Check if the value is properly set.

        Parameters
        ----------
        name : str
            The name of the value.

        Raises
        ------
        TypeError
            If the value is not a distribution.
        """
        logger.info(f"Checking parameter value '{name}'.")
        if not isinstance(self["val"], DistABC):
            raise TypeError(f"Specified value for '{name}' is not a distribution.")

    def to_pro_param(self, **kwargs):
        """Return ``None``."""
        return None

    def to_py_param(self, **kwargs):
        """Return ``None``."""
        return None

    def set(self, val):
        """Set the random value.

        Parameters
        ----------
        val : shamo.DistABC
            The random value.
        """
        self["val"] = val

    def to_param(self, name="", **kwargs):
        """Return the fixed and varying parameters separately.

        Parameters
        ----------
        name : str
            The name of the property.

        Returns
        -------
        list [list [str, list [float, str | None]]]
            The fixed parameters.
        list [list [str, list [shamo.DistABC, str | None]]]
            The varying parameters.
        """
        fixed = []
        varying = []
        name = f"{name}.val"
        if self.val.dist_type == DistABC.TYPE_CONSTANT:
            return [[name, [self.val.val, None]]], []
        else:
            return [], [[name, [self.val, None]]]
