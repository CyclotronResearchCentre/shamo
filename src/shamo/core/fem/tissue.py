"""Implement the `Tissue` class."""
from . import Group, Field


class Tissue(dict):
    """A FEM tissue.

    Parameters
    ----------
    surf : dict [str, int or Iterable [int]] or shamo.fem.Group
        The surface physical group of the tissue.
    vol : dict [str, int or Iterable [int]] or shamo.fem.Group
        The volume physical group of the tissue.
    fields : dict [str, *]
        The fields defined in th tissue.
    """

    def __init__(self, surf, vol, fields={}):
        super().__init__(
            {
                "surf": Group(**surf),
                "vol": Group(**vol),
                "fields": {n: Field(**f) for n, f in fields.items()},
            }
        )

    @property
    def surf(self):
        """Return the surface group of the tissue.

        Returns
        -------
        shamo.fem.Group
            The surface group of the tissue.
        """
        return self["surf"]

    @property
    def vol(self):
        """Return the volume group of the tissue.

        Returns
        -------
        shamo.fem.Group
            The volume group of the tissue.
        """
        return self["vol"]

    @property
    def fields(self):
        """Return the fields of the tissue.

        Returns
        -------
        dict [str, shamo.fem.Field]
            The fields of the tissue.
        """
        return self["fields"]
