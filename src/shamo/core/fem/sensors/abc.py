"""Implement the `Sensor` class."""


class SensorABC(dict):
    """A FEM sensor.

    Parameters
    ----------
    tissue : str
        The tissue the sensor is in.
    real_coords : Iterable [float]
        The coordinates of the sensor in the real world.
    mesh_coords : Iterable [float]
        The coordinates of the sensor in the mesh.
    sensor_type : str
        The type of the sensor.
    """

    TYPE_POINT = "point"
    TYPE_CIRCLE = "circle"

    def __init__(self, tissue, sensor_type, real_coords, mesh_coords):
        super().__init__(
            {
                "tissue": tissue,
                "sensor_type": sensor_type,
                "real_coords": tuple(real_coords),
                "mesh_coords": tuple(mesh_coords),
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
    def tissue(self):
        """Return the tissue the sensor is in.

        Returns
        -------
        str
            The tissue the sensor is in.
        """
        return self["tissue"]

    @property
    def sensor_type(self):
        """Return the type of the sensor.

        Returns
        -------
        str
            The type of the sensor.
        """
        return self["sensor_type"]

    @staticmethod
    def load(sensor_type, **kwargs):
        from .point import PointSensor
        from .surface import CircleSensor

        sensor_types = {
            SensorABC.TYPE_POINT: PointSensor,
            SensorABC.TYPE_CIRCLE: CircleSensor,
        }
        return sensor_types[sensor_type](**kwargs)
