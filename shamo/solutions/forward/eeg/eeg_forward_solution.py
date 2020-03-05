"""Implement `EEGForwardSolution` class.

This module implements the `EEGForwardSolution` class which holds the data
corresponding to the solution of the EEG forward problem.
"""
import numpy as np
from scipy.spatial.distance import cdist

from shamo.solutions import ForwardSolution


class EEGForwardSolution(ForwardSolution):

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
            If set to `True`, matrix is never loaded in memory. (The default
            is `False`)

        Returns
        -------
        dict[str: float]
            The recordings for each active sensor [V].
        """
        recordings = {}
        matrix = self.get_matrix(memory_map=memory_map)
        for i_sensor, name in enumerate(self.sensors):
            recordings[name] = float(np.dot(matrix[i_sensor, :],
                                            sources_vector))
        return recordings

    def evaluate_for_elements(self, element_sources):
        """Evaluate the leadfield matrix for a set of sources.

        Parameters
        ----------
        element_sources : dict[int, tuple[float, float, float]]
            A dictionary containing element tags as keys and source values as
            values [Am].

        Returns
        -------
        dict[str: float]
            The recordings for each active sensor.
        """
        # Generate sources vector
        sources_vector = np.zeros((self.shape[1],))
        element_tags = self.get_elements(coords=False)
        for element_tag, values in element_sources.items():
            element_index = \
                np.argwhere(element_tags == element_tag).flatten()[0]
            offset = element_index * self.n_values_per_element
            sources_vector[offset:offset + self.n_values_per_element] = values
        return self.evaluate(sources_vector)

    def evaluate_for_sources(self, sources):
        """Evaluate the leadfield matrix for a set of sources.

        Parameters
        ----------
        sources : list[shamo.EEGSource]
            The sources for which the leadfield matrix must be evaluated.

        Returns
        -------
        dict[str: float | tuple]
            The recordings for each active sensor.
        """
        # Generate sources vector
        sources_vector = np.zeros((self.shape[1],))
        element_tags, element_coords = self.get_elements()
        for source in sources:
            distances = cdist([source.coordinates], element_coords).flatten()
            element_index = np.argmin(distances)
            offset = element_index * self.n_values_per_element
            sources_vector[offset:offset + self.n_values_per_element] = \
                np.array(source.unit_orientation) * source.value
        return self.evaluate(sources_vector)
