"""Implement the `Sensor` class.

This module implements the `Sensor` class which holds the data corresponding
to a sensor.
"""
import numpy as np


class Sensor(dict):
    """Store sensor information.

    Parameters
    ----------
    real_coordinates : Tuple(float, float, float)
        The coordinates in the real world.
    mesh_coordinates : Tuple(float, float, float)
        The coordinates in the mesh.
    group : int
        The physical tag.
    entity : int
        The geometric tag.
    on_tissue : str
        The name of the tissue the sensor is placed on.

    Attributes
    ----------
    real_coordinates
    mesh_coordinates
    group
    entity
    on_tissue
    coordinates_error
    """

    def __init__(self, real_coordinates, mesh_coordinates, group, entity,
                 on_tissue):
        super().__init__()
        self["real_coordinates"] = tuple(real_coordinates)
        self["mesh_coordinates"] = tuple(mesh_coordinates)
        self["group"] = group
        self["entity"] = entity
        self["on_tissue"] = on_tissue

    # PROPERTIES --------------------------------------------------------------
    @property
    def real_coordinates(self):
        """Return the real coordinates of the sensor.

        Returns
        -------
        Tuple(float, float, float)
            The real coordinates of the sensor.
        """
        return self["real_coordinates"]

    @property
    def mesh_coordinates(self):
        """Return the mesh coordinates of the sensor.

        Returns
        -------
        Tuple(float, float, float)
            The mesh coordinates of the sensor.
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
        difference = np.abs(np.array(self.real_coordinates)
                            - np.array(self.mesh_coordinates))
        return np.linalg.norm(difference)
