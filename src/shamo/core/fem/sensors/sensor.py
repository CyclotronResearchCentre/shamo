"""Implement the `Sensor` class."""


class Sensor(dict):
    """A FEM sensor.

    Parameters
    ----------
    tissue : str
        The tissue the sensor is in.
    sensor_type : str
        The type of the sensor.
    """

    TYPE_POINT = "point"

    def __init__(self, tissue, sensor_type):
        super().__init__({"tissue": tissue, "sensor_type": sensor_type})

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
