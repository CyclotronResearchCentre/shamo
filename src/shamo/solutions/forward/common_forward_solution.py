"""Implement `CommonForwardSolution` class.

This module implements the `CommonForwardSolution` class which is the base for
any `ForwardSolution` or `PArametricForwardSolution`.
"""
from pathlib import Path

import numpy as np

from shamo.core import Solution
from shamo.utils import get_relative_path


class CommonForwardSolution(Solution):
    """The base for any forward problem solution.

    Parameters
    ----------
    name : str
        The name of the solution.
    parent_path : str
        The path to the parent directory of the solution.

    Other Parameters
    ----------------
    problem : dict [str, Any]
        The problem that result in this solution.
    model_path : PathLike
        The path to the model file.
    shape : tuple (int, int)
        The shape of the matrix.
    sensors : list [str]
        The names of the sensors.
    n_sensors : int
        The number of sensors.
    n_elements : int
        The number of elements.
    n_values_per_element : int
        The number of values by element.
    elements_path : PathLike
        The path to the elements file.

    See Also
    --------
    shamo.solutions.forward.common_forward_solution.CommonForwardSolution
    """

    N_VALUES_PER_ELEMENT = 0

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        # Shape
        self["shape"] = tuple(kwargs.get("shape", (0, 0)))
        # Sensors
        self["sensors"] = kwargs.get("sensors", [])
        # Elements path
        elements_path = kwargs.get("elements_path", None)
        if elements_path is not None:
            self["elements_path"] = str(Path(elements_path))
        else:
            self["elements_path"] = None

    @property
    def shape(self):
        """Return the shape of the matrix.

        Returns
        -------
        tuple (int, int)
            The shape of the matrix.
        """
        return self["shape"]

    @property
    def n_sensors(self):
        """Return the number of sensors.

        Returns
        -------
        int
            The number of sensors.
        """
        return self.shape[0]

    @property
    def n_elements(self):
        """Return the number of elements.

        Returns
        -------
        int
            The number of elements.
        """
        return int(self.shape[1] / self.N_VALUES_PER_ELEMENT)

    @property
    def n_values_per_element(self):
        """Return the number of values by element.

        Returns
        -------
        int
            The number of values by element.
        """
        return self.N_VALUES_PER_ELEMENT

    @property
    def sensors(self):
        """Return the names of the sensors.

        Returns
        -------
        list [str]
            The names of the sensors.
        """
        return self["sensors"]

    @property
    def elements_path(self):
        """Return the path to the elements file.

        Returns
        -------
        str
            The path to the elements file.

        Raises
        ------
        FileNotFoundError
            If the model does not contain elements.
            If the elements file does not exist.
        """
        # Check if the elements file exists
        if self["elements_path"] is None:
            raise FileNotFoundError("The model does not contain a FE model.")
        path = Path(self.path) / self["elements_path"]
        if not path.exists():
            raise FileNotFoundError(
                ("The specified elements file no longer " "exists.")
            )
        return str(path)

    def set_elements_path(self, elements_path):
        """Set the path to elements file.

        Parameters
        ----------
        elements_path : PathLike
            The path to elements file.

        Returns
        -------
        shamo.solutions.forward.common_forward_solution.CommonForwardSolution
            The solution.
        """
        self["elements_path"] = get_relative_path(elements_path, self.path)
        return self

    def set_elements(self, element_tags, element_coords):
        """Set the elements.

        Parameters
        ----------
        element_tags : numpy.ndarray
            The tags of the elements.
        element_coords : numpy.ndarray
            The coordinates of the elements.

        Returns
        -------
        shamo.solutions.forward.common_forward_solution.CommonForwardSolution
            The solution.
        """
        elements_path = str(Path(self.path) / "{}_elements.npz".format(self.name))
        self["elements_path"] = str(Path(elements_path).relative_to(self.path))
        np.savez(elements_path, tags=element_tags, coords=element_coords)
        return self

    def get_elements(self, tags=True, coords=True):
        """Return the elements information.

        Parameters
        ----------
        tags : bool, optional
            If set to ``True``, return the tags of the elements.
            (The default is ``True``)
        coords : bool, optional
            If set to ``True``, return the coordinates of the elements.
            (The default is ``True``)

        Returns
        -------
        numpy.ndarray
            If ``tags`` is ``True``, the tags of the elements.
        numpy.ndarray
            If ``coords`` is ``True``, the coordinates of the elements.
        """
        values = []
        elements = np.load(self.elements_path)
        if tags:
            values.append(elements["tags"])
        if coords:
            values.append(elements["coords"])
        if len(values) > 1:
            return values
        return values[0]

    def set_sensors(self, sensors):
        """Set the names of the sensors used to generate the foward model.

        Parameters
        ----------
        sensors : list [str]
            The names of the sensors used to generate the foward model.

        Returns
        -------
        shamo.solutions.forward.common_forward_solution.CommonForwardSolution
            The solution.
        """
        if self.n_sensors != 0:
            if len(sensors) != self.n_sensors:
                raise ValueError("Sensors count not matching matrix shape.")
        self["sensors"] = sensors
        return self
