"""Implement the `Sensor` class.

This module implements the `Sensor` class which holds the data corresponding
to a sensor.
"""
import numpy as np


class Sensor(dict):
    """Store sensor information.

    Parameters
    ----------
    real_coordinates : tuple (float, float, float)
        The coordinates in the real world [m].
    mesh_coordinates : tuple (float, float, float)
        The coordinates in the mesh [m].
    group : int
        The physical tag.
    entity : int
        The geometric tag.
    on_tissue : str
        The name of the tissue the sensor is placed on.
    """

    def __init__(
        self, real_coordinates, mesh_coordinates, group, entity, node, on_tissue
    ):
        super().__init__()
        self["real_coordinates"] = tuple([float(i) for i in real_coordinates])
        self["mesh_coordinates"] = tuple([float(i) for i in mesh_coordinates])
        self["group"] = int(group)
        self["entity"] = int(entity)
        self["node"] = int(node)
        self["on_tissue"] = on_tissue

    # PROPERTIES --------------------------------------------------------------
    @property
    def real_coordinates(self):
        """Return the real coordinates of the sensor.

        Returns
        -------
        tuple (float, float, float)
            The real coordinates of the sensor [m].
        """
        return self["real_coordinates"]

    @property
    def mesh_coordinates(self):
        """Return the mesh coordinates of the sensor.

        Returns
        -------
        tuple (float, float, float)
            The mesh coordinates of the sensor [m].
        """
        return self["mesh_coordinates"]

    @property
    def group(self):
        """Return the physical group of the sensor.

        Returns
        -------
        int
            The physical group of the sensor.
        """
        return self["group"]

    @property
    def entity(self):
        """Return the entity tag of the sensor.

        Returns
        -------
        int
            The entity tag of the sensor.
        """
        return self["entity"]

    @property
    def node(self):
        """Return the node tag of the sensor.

        Returns
        -------
        int
            The node tag of the sensor.
        """
        return self["node"]

    @property
    def on_tissue(self):
        """Return the name of the tissue the sensor is placed on.

        Returns
        -------
        str
            The name of the tissue the sensor is placed on.
        """
        return self["on_tissue"]

    @property
    def coordinates_error(self):
        """Return the error of coordinates.

        Return the distance between the real coordinates and the mesh
        coordinates in millimeters.

        Returns
        -------
        float
            The error of coordinates.
        """
        difference = (
            np.abs(np.array(self.real_coordinates) - np.array(self.mesh_coordinates))
            * 1000
        )
        return np.linalg.norm(difference)
