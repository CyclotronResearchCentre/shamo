"""Implement `ForwardSolution` class.

This module implements the `ForwardSolution` class which is the base for any
forward problem solution.
"""
from pathlib import Path

import numpy as np

from shamo.core import Solution
from shamo.utils import get_relative_path


class ForwardSolution(Solution):
    """The base for any forward problem solution.

    Parameters
    ----------
    name : str
        The name of the solution.
    parent_path : str
        The path to the parent directory of the solution.

    Attributes
    ----------
    problem

    Other Parameters
    ----------------
    problem : dict[str: Any]
        The problem that result in this solution.
    matrix_path : PathLike
        The path to the matrix file.
    shape : tuple[int, int]
        The shape of the matrix.
    sensors : list[str]
        The names of the sensors.
    n_sensors : int
        The number of sensors.
    n_elements : int
        The number of elements.
    n_values_per_element : int
        The number of values by element.
    model_path : PathLike
        The path to the
    """

    N_VALUES_PER_ELEMENT = 0

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        # Matrix path
        matrix_path = kwargs.get("matrix_path", None)
        if matrix_path is not None:
            self["matrix_path"] = str(Path(matrix_path))
        else:
            self["matrix_path"] = None
        # Shape
        self["shape"] = tuple(kwargs.get("shape", (0, 0)))
        # Sensors
        self["sensors"] = kwargs.get("sensors", [])
        # Model path
        model_path = kwargs.get("model_path", None)
        if model_path is not None:
            self["model_path"] = str(Path(model_path))
        else:
            self["model_path"] = None
        # Elements path
        elements_path = kwargs.get("elements_path", None)
        if elements_path is not None:
            self["elements_path"] = str(Path(elements_path))
        else:
            self["elements_path"] = None

    @property
    def matrix_path(self):
        """Return the path to matrix file.

        Returns
        -------
        str
            The path to matrix file.

        Raises
        ------
        FileNotFoundError
            If the model does not contain a matrix file.
            If the matrix file does not exist.
        """
        # Check if the matrix file exists
        if self["matrix_path"] is None:
            raise FileNotFoundError("The model does not contain a matrix.")
        path = Path(self.path) / self["matrix_path"]
        if not path.exists():
            raise FileNotFoundError(("The specified matrix file no longer "
                                     "exists."))
        return str(path)

    @property
    def shape(self):
        """Return the shape of the matrix.

        Returns
        -------
        tuple[int, int]
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
        list[str]
            The names of the sensors.
        """
        return self["sensors"]

    @property
    def model_path(self):
        """Return the path to the FE model file.

        Returns
        -------
        str
            The path to the FE model file.

        Raises
        ------
        FileNotFoundError
            If the model does not contain a FE model.
            If the FE model file does not exist.
        """
        # Check if the model file exists
        if self["model_path"] is None:
            raise FileNotFoundError("The model does not contain a FE model.")
        path = Path(self.path) / self["model_path"]
        if not path.exists():
            raise FileNotFoundError(("The specified FE model file no longer "
                                     "exists."))
        return str(path)

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
            raise FileNotFoundError(("The specified elements file no longer "
                                     "exists."))
        return str(path)

    def set_matrix(self, matrix):
        """Set the matrix.

        Parameters
        ----------
        matrix : numpy.ndarray
            The matrix.

        Returns
        -------
        shamo.solutions.ForwardSolution
            The solution.
        """
        matrix_name = "{}_matrix.npy".format(self.name)
        matrix_path = str(Path(self.path) / matrix_name)
        self["matrix_path"] = matrix_name
        np.save(matrix_path, matrix)
        self["shape"] = matrix.shape
        return self

    def get_matrix(self, memory_map=False):
        """Return the matrix.

        Parameters
        ----------
        memory_map : bool, optional
            If set to `True`, the returned array is mapped on memory. (The
            default is `False`)

        Returns
        -------
        numpy.ndarray
            The matrix.
        """
        memory_map_mode = "r" if memory_map else None
        return np.load(self.matrix_path, mmap_mode=memory_map_mode)

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
        shamo.solutions.ForwardSolution
            The solution.
        """
        elements_path = str(Path(self.path)
                            / "{}_elements.npz".format(self.name))
        self["elements_path"] = str(Path(elements_path).relative_to(self.path))
        np.savez(elements_path, tags=element_tags, coords=element_coords)
        return self

    def get_elements(self, tags=True, coords=True):
        """Return the elements information.

        Parameters
        ----------
        tags : bool, optional
            If set to `True`, return the tags of the elements.
            (The default is `True`)
        coords : bool, optional
            If set to `True`, return the coordinates of the elements.
            (The default is `True`)

        Returns
        -------
        numpy.ndarray
            If `tags` is `True`, the tags of the elements.
        numpy.ndarray
            If `coords` is `True`, the coordinates of the elements.
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

    def set_model(self, model):
        """Set the FE model used to generate the forward model.

        Parameters
        ----------
        model : shamo.FEModel
            The model used to generate the forward model.

        Returns
        -------
        shamo.model.ForwardModel
            The solution.
        """
        self["model_path"] = get_relative_path(model.json_path, self.path)
        return self

    def set_sensors(self, sensors):
        """Set the names of the sensors used to generate the foward model.

        Parameters
        ----------
        sensors : list[str]
            The names of the sensors used to generate the foward model.

        Returns
        -------
        shamo.model.ForwardModel
            The solution.
        """
        if self.n_sensors != 0:
            if len(sensors) != self.n_sensors:
                raise ValueError("Sensors count not matching matrix shape.")
        self["sensors"] = sensors
        return self
