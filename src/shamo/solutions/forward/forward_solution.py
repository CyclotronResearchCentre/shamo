"""Implement `ForwardSolution` class.

This module implements the `ForwardSolution` class which is the base for any
forward problem solution.
"""
import abc
from pathlib import Path

import numpy as np

from shamo.solutions import CommonForwardSolution


class ForwardSolution(CommonForwardSolution):
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
    matrix_path : PathLike
        The path to the matrix file.
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
    shamo.solutions.CommonForwardSolution
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        # Matrix path
        matrix_path = kwargs.get("matrix_path", None)
        if matrix_path is not None:
            self["matrix_path"] = str(Path(matrix_path))
        else:
            self["matrix_path"] = None

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
            raise FileNotFoundError(("The specified matrix file no longer " "exists."))
        return str(path)

    def set_matrix(self, matrix):
        """Set the matrix.

        Parameters
        ----------
        matrix : numpy.ndarray
            The matrix.

        Returns
        -------
        shamo.solutions.forward.forward_solution.ForwardSolution
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
            If set to ``True``, the returned array is mapped on memory. (The
            default is ``False``)

        Returns
        -------
        numpy.ndarray
            The matrix.
        """
        memory_map_mode = "r" if memory_map else None
        return np.load(self.matrix_path, mmap_mode=memory_map_mode)

    @abc.abstractmethod
    def evaluate(self, sources_vector, memory_map=False):
        """Evaluate the leadfield matrix for a set of sources.

        Parameters
        ----------
        sources_vector : numpy.ndarray
            The s vector from L.s=r.
        memory_map : bool, optional
            If set to ``True``, matrix is never loaded in memory. (The default
            is ``False``)

        Returns
        -------
        dict [str, float | tuple]
            The recordings for each active sensor.
        """

    @abc.abstractmethod
    def evaluate_for_elements(self, element_sources):
        """Evaluate the leadfield matrix for a set of sources.

        Parameters
        ----------
        element_sources : dict[int, tuple[float, float, float]]
            A dictionary containing element tags as keys and source values as
            values.

        Returns
        -------
        dict [str, float|tuple]
            The recordings for each active sensor.
        """

    @abc.abstractmethod
    def evaluate_for_sources(self, sources):
        """Evaluate the leadfield matrix for a set of sources.

        Parameters
        ----------
        sources : list [shamo.model.sources.source.Source]
            The sources for which the leadfield matrix must be evaluated.

        Returns
        -------
        dict [str, float|tuple]
            The recordings for each active sensor.
        """
