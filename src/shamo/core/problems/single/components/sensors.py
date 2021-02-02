"""Implement the `CompSensor` class."""
import logging

from .abc import CompABC
from shamo.core import SensorABC

logger = logging.getLogger(__name__)


class CompSensors(CompABC):
    """Store information about a list of sensors.

    Other Parameters
    ----------------
    sensors : list [str]
        A list of sensor names.
    """

    def __init__(self, **kwargs):
        super().__init__(sensors=kwargs.get("sensors", []))

    def check(self, name, **kwargs):
        """Check if the list of sensors is properly set.

        Parameters
        ----------
        name : str
            The name of the list of sensors.

        Raises
        ------
        RuntimeError
            If an element in the list is not in the model.

        Other Parameters
        ----------------
        sensors : dict [str, shamo.Sensor]
            The sensors of the model.
        """
        logger.info(f"Checking sensors '{name}'.")
        sensors = kwargs.get("sensors", {})
        for s in self["sensors"]:
            if s not in sensors:
                raise RuntimeError(f"Sensor '{s}' not found in model.")

    def to_pro_param(self, **kwargs):
        """Return the sensors required to produce the PRO file.

        Returns
        -------
        dict [str, list [dict [str, int]]]
            The sensors names and physical points.

        Other Parameters
        ----------------
        sensors : dict [str, shamo.Sensor]
            The sensors of the model.
        """
        sensors = kwargs.get("sensors", {})
        point = []
        real = []
        for s in self["sensors"]:
            if sensors[s].sensor_type == SensorABC.TYPE_POINT:
                point.append({"sensor": sensors[s].point.group})
            elif sensors[s].sensor_type in [SensorABC.TYPE_CIRCLE]:
                real.append({"sensor": sensors[s].surf.group})
        return {"point": point, "real": real}

    def to_py_param(self, **kwargs):
        """Return the list of sensor names.

        Returns
        -------
        list [str]
            The list of sensor names.
        """
        return self["sensors"]

    def add(self, sensor):
        """Add a sensor to the list.

        Parameters
        ----------
        sensor : str
            The name of the sensor.
        """
        self["sensors"].append(sensor)

    def adds(self, sensors):
        """Add multiple sensors to the list.

        Parameters
        ----------
        sensors : list [str]
            The sensor names.
        """
        self["sensors"].extend(sensors)
