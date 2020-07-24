"""Implement the `Tissue` class.

This module implements the `Tissue` class which holds the data corresponding
to a tissue.
"""


class Tissue(dict):
    """Store tissue information.

    Parameters
    ----------
    volume_group : int
        The physical tag of the volume.
    volume_entity : list [int]
        The geometric tags of the volumes.
    surface_group : int
        The physical tag of the surface.
    surface_entity : list [int]
        The geometric tags of the surfaces.
    """

    def __init__(self, volume_group, volume_entity, surface_group, surface_entity):
        super().__init__()
        self["volume_group"] = int(volume_group)
        self["volume_entity"] = [int(entity) for entity in volume_entity]
        self["surface_group"] = int(surface_group)
        self["surface_entity"] = [int(entity) for entity in surface_entity]

    @property
    def volume_group(self):
        """Return the physical group of the volume.

        Returns
        -------
        int
            The physical group of the volume.
        """
        return self["volume_group"]

    @property
    def volume_entity(self):
        """Return the entity tag of the volume.

        Returns
        -------
        int
            The entity tag of the volume.
        """
        return self["volume_entity"]

    @property
    def surface_group(self):
        """Return the physical group of the surface.

        Returns
        -------
        int
            The physical group of the surface.
        """
        return self["surface_group"]

    @property
    def surface_entity(self):
        """Return the entity tag of the surface.

        Returns
        -------
        int
            The entity tag of the surface.
        """
        return self["surface_entity"]
