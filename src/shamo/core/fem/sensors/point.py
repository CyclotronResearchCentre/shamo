"""Implement the `PointSensor` class."""
from collections.abc import Iterable

from shamo.core.fem import SensorABC, Group


class PointSensor(SensorABC):
    """A FEM sensor.

    Parameters
    ----------
    tissue : str
        The tissue the sensor is in.
    point : shamo.fem.Group
        The physical group of the sensor.
    node : int
        The tag of the node corresponding to the sensor.
    """

    def __init__(self, tissue, real_coords, mesh_coords, point, node, **kwargs):
        super().__init__(tissue, SensorABC.TYPE_POINT, real_coords, mesh_coords)
        self.update({"point": Group(**point), "node": int(node)})

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
