"""Implement `TissueProperty` class.

This module implements the `TissueProperty` class which holds the data
corresponding to a certain property of a tissue.
"""

from shamo.core.distribution import Distribution


class TissueProperty(dict):
    """A tissue property.

    Parameters
    ----------
    value : object
        The value of the property.
    anisotropy : str, optional
        The name of the anisotropy field used for this property. (The default
        is ``''``)
    """

    def __init__(self, value, anisotropy=""):
        super().__init__()
        if isinstance(value, dict):
            self["value"] = Distribution.load(value)
        else:
            self["value"] = value
        self["anisotropy"] = anisotropy

    @property
    def value(self):
        """Return the value of the property.

        Returns
        -------
        object
            The value of the property.
        """
        return self["value"]

    @property
    def anisotropy(self):
        """Return the name of the anisotropy field used for this property.

        Returns
        -------
        str
            The name of the anisotropy field used for this property. If no
            anisotropy is specified, return ``''``.
        """
        return self["anisotropy"]

    @property
    def is_anisotropic(self):
        """Return wether the property is anisotropic.

        Returns
        -------
        bool
            Return ``True`` if the property is anisotropic, otherwise return
            ``False``.
        """
        if self.anisotropy == "":
            return False
        return True
