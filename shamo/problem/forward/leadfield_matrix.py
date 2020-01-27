"""Implement `LeadfieldMatrix`class.

This module implements the `LeadfieldMatrix`class which is the base class for
any forward problem solution.
"""
from pathlib import Path

import numpy as np
from scipy.interpolate import griddata

from shamo.core import JSONObject
from shamo.core.utils import get_relative_path


class LeadfieldMatrix(JSONObject):
    """Base class for any leadfield matrix.

    Parameters
    ----------
    name : str
        The name of the leadfield matrix.
    parent_path : str
        The path to the parent directory of the leadfield matrix.
    parents : bool
        If set to `True`, any missing level in the tree is created. (The
        default is `True`).
    exist_ok : bool
        If set to `True`, no exception is raised if the directory already
        exists. (The default is `True`).
    matrix_path : str, optional
        The path to the matrix file. (The default is `None`).
    shape : tuple[int, int], optional
        The shape of the matrix. (The default is `None`).
    sensor_names : list[str], optional
        The ordered names of the sensors used for the leadfield matrix. (The
        default is `None`).
    settings : shamo.problem.forward.ForwardProblem, optional
        The solved forward problem. (The default is `None`).
    model_path : str, optional
        The path to the model used to solve the problem. (The default is
        `None`).

    Attributes
    ----------
    name
    path
    json_path
    matrix_path
    shape
    n_sensors
    n_elements
    elements_path
    sensors_names
    settings
    model_path
    """

    N_VALUES_PER_ELEMENT = 0

    def __init__(self, name, parent_path, parents=True, exist_ok=True,
                 matrix_path=None, shape=None, elements_path=None,
                 sensor_names=None, settings=None, model_path=None):
        super().__init__(name, parent_path, parents, exist_ok)
        if matrix_path is not None:
            self["matrix_path"] = matrix_path
        if shape is not None:
            self["shape"] = tuple(shape)
        if elements_path is not None:
            self["elements_path"] = elements_path
        if sensor_names is not None:
            self["sensor_names"] = sensor_names
        if settings is not None:
            self["settings"] = settings
        if model_path is not None:
            self["model_path"] = model_path

    @property
    def matrix_path(self):
        """Return the path to matrix file.

        Returns
        -------
        str
            The path to matrix file.
        """
        matrix_path = self.get("matrix_path", None)
        if matrix_path is not None:
            return str((Path(self.path) / matrix_path))
        return None

    @property
    def shape(self):
        """Return the shape of the matrix.

        Returns
        -------
        tuple[int, int]
            The shape of the matrix.
        """
        return self.get("shape", None)

    @property
    def n_sensors(self):
        """Return the number of sensors.

        Returns
        -------
        int
            The number of sensors.
        """
        if self.shape is not None:
            return self.shape[0]
        return None

    @property
    def n_elements(self):
        """Return the number of elements.

        Returns
        -------
        int
            The number of elements.
        """
        if self.shape is not None:
            return int(self.shape[1] / self.N_VALUES_PER_ELEMENT)
        return None

    @property
    def elements_path(self):
        """Return the path to elements file.

        Returns
        -------
        str
            The path to elements file.
        """
        elements_path = self.get("elements_path", None)
        if elements_path is not None:
            return str(Path(self.path) / elements_path)
        return None

    @property
    def sensor_names(self):
        """Return the names of the active sensors.

        Returns
        -------
        list[str]
            The names of the active sensors.
        """
        return self.get("sensor_names", None)

    @property
    def settings(self):
        """Return the settings used to produce the leadfield matrix.

        Returns
        -------
        dict[str: Any]
            The settings used to produce the leadfield matrix.
        """
        return self.get("settings", None)

    @property
    def model_path(self):
        """Return the path to the model `.json` file.

        Returns
        -------
        str
            The path to the model `.json` file.
        """
        model_path = self.get("model_path", None)
        if model_path is not None:
            return str((Path(self.path) / model_path))
        return None

    def set_matrix(self, matrix):
        """Set the leadfield matrix.

        Parameters
        ----------
        matrix : numpy.ndarray
            The leadfield matrix.

        Returns
        -------
        shamo.problem.forward.LeadfieldMatrix
            The current leadfield matrix.
        """
        matrix_path = str(Path(self.path) / "{}_matrix.npy".format(self.name))
        self["matrix_path"] = str(Path(matrix_path).relative_to(self.path))
        self["shape"] = matrix.shape
        np.save(matrix_path, matrix)
        return self

    def get_matrix(self, memory_map=False):
        """Return the matrix.

        Parameters
        ----------
        memory_map : bool, optional
            If set to `True`, the returned array is mapped on memory. (The
            default is `False`).

        Returns
        -------
        numpy.ndarray
            The matrix.
        """
        memory_map_mode = "r" if memory_map else None
        return np.load(self.matrix_path, mmap_mode=memory_map_mode)

    def interpolate_matrix(self, on_coordinates):
        """Resample the matrix on given coordinates.

        Parameters
        ----------
        on_coordinates : numpy.ndarray
            The coordinates to sample the matrix on.

        Returns
        -------
        numpy.ndarray
            The resampled matrix.
        """
        _, from_coordinates = self.get_elements()
        undersampled_matrix = self.get_matrix().T
        n_rows = int(self.n_elements)
        n_cols = int(self.n_sensors * self.N_VALUES_PER_ELEMENT)
        # Reshape input values
        from_values = np.empty((n_rows, n_cols))
        for i in range(self.N_VALUES_PER_ELEMENT):
            undersampled_slice = np.arange(i, undersampled_matrix.shape[0],
                                           self.N_VALUES_PER_ELEMENT)
            from_values[:, i*self.n_sensors:(i+1)*self.n_sensors] = \
                undersampled_matrix[undersampled_slice, :]
        # Generate upsampled values
        interpolated_values = griddata(from_coordinates, from_values,
                                       on_coordinates, method="linear")
        nan_indices = np.argwhere(np.isnan(interpolated_values[:, 0]))
        nan_coordinates = on_coordinates[nan_indices]
        interpolated_values[nan_indices, :] = griddata(
            from_coordinates, from_values, nan_coordinates, method="nearest")
        # Reshape output values
        matrix = np.empty((on_coordinates.shape[0] * 3, self.n_sensors))
        for i in range(self.N_VALUES_PER_ELEMENT):
            matrix_slice = np.arange(i, matrix.shape[0],
                                     self.N_VALUES_PER_ELEMENT)
            matrix[matrix_slice, :] = \
                interpolated_values[:, i*self.n_sensors:(i+1)*self.n_sensors]
        return matrix.T

    def get_full_matrix(self):
        """Generate the full matrix from undersampled one.

        Returns
        -------
        numpy.ndarray
            The full matrix.
        """
        _, _, _, all_coordinates = self.get_elements(all=True)
        return self.interpolate_matrix(all_coordinates)

    def set_elements(self, elements, element_coordinates, all_elements=None,
                     all_element_coordinates=None):
        """Set the elements on which the leadfield matrix is computed.

        Parameters
        ----------
        elements: numpy.ndarray
            The tags of the elements.
        element_coordinates: numpy.ndarray
            The coordinates of the elements.
        all_elements: numpy.ndarray, optional
            The tags of the unsampled elements. (The default is `None`).
        all_element_coordinates: numpy.ndarray, optional
            The coordinates of the unsampled elements. (The default is `None`).

        Returns
        -------
        shamo.problem.forward.LeadfieldMatrix
            The current leadfield matrix.
        """
        elements_path = str((Path(self.path)
                             / "{}_elements.npz".format(self.name)))
        self["elements_path"] = str(Path(elements_path).relative_to(self.path))
        if all_elements is None:
            np.savez(elements_path, tags=elements,
                     coordinates=element_coordinates)
        else:
            np.savez(elements_path, tags=elements,
                     coordinates=element_coordinates, all_tags=all_elements,
                     all_coordinates=all_element_coordinates)
        return self

    def get_elements(self, all=False):
        """Return the matrix.

        Parameters
        ----------
        all : bool, optional
            If set to `True`, return also the tags and coordinates of the
            unsampled elements. (The default is `False`).

        Returns
        -------
        numpy.ndarray
            The tags of the elements used in the matrix.
        numpy.ndarray
            The coordinates of the elements used in the matrix.
        numpy.ndarray
            The tags of all the elements.
        numpy.ndarray
            The coordinates of all the elements.
        """
        elements = np.load(self.elements_path)
        if all:
            return (elements["tags"], elements["coordinates"],
                    elements.get("all_tags", None),
                    elements.get("all_coordinates", None))
        return elements["tags"], elements["coordinates"]

    def set_elements_path(self, elements_path):
        """Set the path to the elements file.

        Parameters
        ----------
        elements_path: str
            The path to the elements file.

        Returns
        -------
        shamo.problem.forward.LeadfieldMatrix
            The current leadfield matrix.
        """
        self["elements_path"] = get_relative_path(elements_path, self.path)
        return self

    def set_sensor_names(self, sensor_names):
        """Set the names of the active sensors.

        Parameters
        ----------
        sensor_names: list[str]
            The names of the active sensors.

        Returns
        -------
        shamo.problem.forward.LeadfieldMatrix
            The current leadfield matrix.
        """
        self["sensor_names"] = sensor_names
        return self

    def set_model(self, model):
        """Set the model used to generate the leadfield matrix.

        Parameters
        ----------
        model: shamo.model.FEModel
            The model used to generate the leadfield matrix.

        Returns
        -------
        shamo.problem.forward.LeadfieldMatrix
            The current leadfield matrix.
        """
        self["model_path"] = get_relative_path(model.json_path, self.path)
        return self
