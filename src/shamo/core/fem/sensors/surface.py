"""Implement the `SurfSensorABC` and `CircleSensor` classes."""
from shamo.core.fem import SensorABC, Group


class SurfSensorABC(SensorABC):
    """The base class for any surfacic sensor.

    Parameters
    ----------
    tissue : str
        The tissue the sensor is in.
    real_coords : Iterable [float]
        The coordinates of the sensor in the real world.
    mesh_coords : Iterable [float]
        The coordinates of the sensor in the mesh.
    surf : shamo.fem.Group
        The physical group of the sensor.
    """

    def __init__(self, tissue, sensor_type, real_coords, mesh_coords, surf, **kwargs):
        super().__init__(tissue, sensor_type, real_coords, mesh_coords)
        self.update(
            {
                "real_coords": tuple(real_coords),
                "mesh_coords": tuple(mesh_coords),
                "surf": Group(**surf),
            }
        )

    @property
    def surf(self):
        """Return the group of the sensor.

        Returns
        -------
        shamo.fem.Group
            The group of the sensor.
        """
        return self["surf"]


class CircleSensor(SurfSensorABC):
    """The base class for any surfacic sensor.

    Parameters
    ----------
    tissue : str
        The tissue the sensor is in.
    real_coords : Iterable [float]
        The coordinates of the sensor in the real world.
    mesh_coords : Iterable [float]
        The coordinates of the sensor in the mesh.
    surf : shamo.fem.Group
        The physical group of the sensor.
    radius : float
        The radius of the sensor.
    """

    def __init__(self, tissue, real_coords, mesh_coords, surf, radius, **kwargs):
        super().__init__(tissue, SensorABC.TYPE_CIRCLE, real_coords, mesh_coords, surf)
        self.update({"radius": float(radius)})

    @property
    def radius(self):
        """Return the radius of the sensor.

        Returns
        -------
        float
            The radius of the sensor.
        """
        return self["radius"]
