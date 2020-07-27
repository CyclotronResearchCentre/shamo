"""Implement `EEGForwardSolution` class.

This module implements the `EEGForwardSolution` class which holds the data
corresponding to the solution of the EEG forward problem.
"""
import numpy as np
from scipy.spatial.distance import cdist

from shamo.solutions import ForwardSolution


class EEGForwardSolution(ForwardSolution):
    """The solution to an EEG forward problem.

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
    model_path : PathLike
        The path to the model file.
    elements_path : PathLike
        The path to the elements file.

    See Also
    --------
    shamo.solutions.forward.forward_solution.ForwardSolution
    """

    from shamo import EEGForwardProblem

    PROBLEM_FACTORY = EEGForwardProblem
    N_VALUES_PER_ELEMENT = 3

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
        dict [str, float]
            The recordings for each active sensor [V].
        """
        recordings = {}
        matrix = self.get_matrix(memory_map=memory_map)
        for i_sensor, name in enumerate(self.sensors):
            recordings[name] = float(np.dot(matrix[i_sensor, :], sources_vector))
        return recordings

    def evaluate_for_elements(self, element_sources):
        """Evaluate the leadfield matrix for a set of sources.

        Parameters
        ----------
        element_sources : dict [int, tuple(float, float, float)]
            A dictionary containing element tags as keys and source values as
            values [Am].

        Returns
        -------
        dict [str, float]
            The recordings for each active sensor.
        """
        # Generate sources vector
        sources_vector = np.zeros((self.shape[1],))
        element_tags = self.get_elements(coords=False)
        for element_tag, values in element_sources.items():
            element_index = np.argwhere(element_tags == element_tag).flatten()[0]
            offset = element_index * self.n_values_per_element
            sources_vector[offset : offset + self.n_values_per_element] = values
        return self.evaluate(sources_vector)

    def evaluate_for_sources(self, sources):
        """Evaluate the leadfield matrix for a set of sources.

        Parameters
        ----------
        sources : list [shamo.model.sources.eeg_source.EEGSource]
            The sources for which the leadfield matrix must be evaluated.

        Returns
        -------
        dict [str, float|tuple]
            The recordings for each active sensor.
        """
        # Generate sources vector
        sources_vector = np.zeros((self.shape[1],))
        element_tags, element_coords = self.get_elements()
        for source in sources:
            distances = cdist([source.coordinates], element_coords).flatten()
            element_index = np.argmin(distances)
            offset = element_index * self.n_values_per_element
            sources_vector[offset : offset + self.n_values_per_element] = source.values
        return self.evaluate(sources_vector)
