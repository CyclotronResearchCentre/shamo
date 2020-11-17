"""Implement the `PointSensor` class."""
from collections.abc import Iterable

from shamo.core.fem import Sensor, Group


class PointSensor(Sensor):
    """A FEM sensor.

    Parameters
    ----------
    tissue : str
        The tissue the sensor is in.
    real_coords : Iterable [float]
        The coordinates of the sensor in the real world.
    mesh_coords : Iterable [float]
        The coordinates of the sensor in the mesh.
    point : shamo.fem.Group
        The physical group of the sensor.
    node : int
        The tag of the node corresponding to the sensor.
    """

    def __init__(self, tissue, real_coords, mesh_coords, point, node, **kwargs):
        super().__init__(tissue, Sensor.TYPE_POINT)
        self.update(
            {
                "real_coords": tuple(real_coords),
                "mesh_coords": tuple(mesh_coords),
                "point": Group(**point),
                "node": int(node),
            }
        )

    @property
    def real_coords(self):
        """Return the real coordinates of the sensor.

        Returns
        -------
        tuple (float, float, float)
            The real coordinates of the sensor [m].
        """
        return self["real_coords"]

    @property
    def mesh_coords(self):
        """Return the mesh coordinates of the sensor.

        Returns
        -------
        tuple (float, float, float)
            The mesh coordinates of the sensor [m].
        """
        return self["mesh_coords"]

    @property
    def point(self):
        """Return the group of the sensor.

        Returns
        -------
        shamo.fem.Group
            The group of the sensor.
        """
        return self["point"]

    @property
    def node(self):
        """Return the node tag of the sensor.

        Returns
        -------
        int
            The node tag of the sensor.
        """
        return self["node"]
