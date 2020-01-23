"""Implement `TissueProperties` class.

This module implements the  `TissueProperties` class which holds the properties
corresponding to a tissue.
"""


class TissueProperties(dict):
    """Store tissue properties.

    Parameters
    ----------
    sigma : float
        The electrical conductivity of the tissue [S/m].
    use_anisotropy : bool, optional
        If set to `True`, anisotropy field is used in the problem. (The
        default is `False`).

    Attributes
    ----------
    sigma
    use_anisotropy
    """

    def __init__(self, sigma, use_anisotropy=False):
        super().__init__()
        self["sigma"] = sigma
        self["use_anisotropy"] = use_anisotropy

    @property
    def sigma(self):
        """Return the electrical conductivity of the tissue.

        Returns
        -------
        float
            The electrical conductivity of the tissue.
        """
        return self["sigma"]

    @property
    def use_anisotropy(self):
        """Return wether the anisotropy field is used or not for the tissue.

        Returns
        -------
        bool
             `True` if the anisotropy field is used for the tissue. `False`
             otherwise.
        """
        return self["use_anisotropy"]
