"""Implement `ForwardProblem`class.

This module implements the `ForwardProblem`class which is the base class for
any forward problem.
"""
import abc

import numpy as np
from scipy.spatial.distance import cdist
import gmsh

from .tissue_properties import TissueProperties


class ForwardProblem(abc.ABC, dict):
    """Base class for any forward problem.

    Parameters
    ----------
    problem_type : str, optional
        The type of forward problem. (The default is `None`).

    tissue_properties : dict[str: dict], optional
        A dictionary containing the name of the tissues as keys and their
        properties as values.

    parameters : dict[str: float | int], optional
        A dictionary containing the name of the parameters as keys and their
        values. (The default is `None`).

    region_of_interest : str | list[str], optional
        When string value is used, the region of interest is the tissue named
        after `region_of_interest`. When list value is used, the region of
        interest is the sum of all the tissues listed by their names. (The
        default is `None`).

    undersampling_distance : float, optional
        The minimum distance between two elements the solution is computed on.
        (The default is `0`).

    Attributes
    ----------
    problem_type
    tissue_properties
    parameters
    region_of_interest
    undersampling_distance

    See Also
    --------
    JSONObject
    """

    TEMPLATE_PATH = ""

    EEG = "eeg"
    MEG = "meg"

    def __init__(self, problem_type=None, tissue_properties={},
                 parameters=None, region_of_interest=None,
                 undersampling_distance=0):
        super().__init__()
        if problem_type is not None:
            self["problem_type"] = problem_type
        self["tissue_properties"] = {name: TissueProperties(**data)
                                     for name, data
                                     in tissue_properties.items()}
        if parameters is not None:
            self["parameters"] = parameters
        if region_of_interest is not None:
            if isinstance(region_of_interest, str):
                self["region_of_interest"] = [region_of_interest]
            elif isinstance(region_of_interest, list):
                self["region_of_interest"] = region_of_interest
            else:
                raise TypeError(("The argument `region_of_interest` must be "
                                 "either of type `str` or `list`."))
        self["undersampling_distance"] = undersampling_distance

    @property
    def problem_type(self):
        """Return the problem type of the forward problem.

        Returns
        -------
        str
            The problem type of the forward problem.
        """
        return self["problem_type"]

    @property
    def tissue_properties(self):
        """Return the tissue properties of the forward problem.

        Returns
        -------
        dict[str: TissueProperties]
            The tissue properties of the forward problem.
        """
        return self["tissue_properties"]

    @property
    def parameters(self):
        """Return the custom parameters of the problem.

        Returns
        -------
        dict[str: Tissue]
            The custom parameters of the problem. If the problem does not have
            any custom parameter, return `None`.
        """
        return self.get("parameters", None)

    @property
    def region_of_interest(self):
        """Return the region of interest of the problem.

        Returns
        -------
        list[str]
            A list of the names of the regions of interest. If the problem does
            not have any custom parameter, return `None`.
        """
        return self.get("region_of_interest", None)

    @property
    def undersampling_distance(self):
        return self["undersampling_distance"]

    def add_tissue(self, name, sigma, use_anisotropy=False):
        """Add a tissue to the problem.

        Parameters
        ----------
        name : str
            The name of the tissue.
        sigma : float
            The electrical conductivity of the tissue [S/m].
        use_anisotropy : bool, optional
            If set to `True`, anisotropy field is used for this tissue. (The
            default is `False`).

        Returns
        -------
        ForwardProblem
            The current forward problem.
        """
        self.tissue_properties[name] = TissueProperties(sigma,
                                                        use_anisotropy)
        return self

    def add_tissues(self, tissue_sigmas, use_anisotropy=False):
        """Add multiple tissues to the problem.

        Parameters
        ----------
        tissue_sigmas : dict[str: float]
            A dictionary containing the names of the tissues as keys and their
            electrical conductivity as values [S/m].
        use_anisotropy : bool | dict, optional
            When boolean value is used, it uses the same value for all the
            tissues. When a dictionary is used, it must contain the name of the
            tissues as keys and boolean values. If a name is present in
            `tissue_sigmas` but not in `use_anisotropy`, it uses the default
            value. If set to `True`, anisotropy field is used for this tissue.
            (The default is `False`).

        Returns
        -------
        ForwardProblem
            The current forward problem.
        """
        if isinstance(use_anisotropy, bool):
            for name, sigma in tissue_sigmas.items():
                self.add_tissue(name, sigma, use_anisotropy)
        elif isinstance(use_anisotropy, dict):
            for name, sigma in tissue_sigmas.items():
                self.add_tissue(name, sigma, use_anisotropy.get(name, False))
        else:
            raise TypeError(("The argument `use_anistropy` must be either of "
                             "type `bool` or `dict`."))
        return self

    def add_parameter(self, name, value):
        """Add a custom parameter to the problem.

        Parameters
        ----------
        name : str
            The name of the parameter.
        value : float | int
            The value of the parameter.

        Returns
        -------
        ForwardProblem
            The current forward problem.

        Notes
        -----
        Custom parameters are passed to `evaluate_formula()` method from
        `Anisotropy` class when `use_anisotropy` is set to `True` for the
        corresponding tissue.
        """
        if self.get("parameters", None) is not None:
            self["parameters"][name] = value
        else:
            self["parameters"] = {name: value}
        return self

    def add_parameters(self, name_values):
        """Add multiple custom parameters to the problem.

        Parameters
        ----------
        name_values : dict[str: float | int]
            A dictionary containing the names of the parameters as keys and
            their values.

        Returns
        -------
        ForwardProblem
            The current forward problem.

        Notes
        -----
        Custom parameters are passed to `evaluate_formula()` method from
        `Anisotropy` class when `use_anisotropy` is set to `True` for the
        corresponding tissue.
        """
        if self.get("parameters", None) is not None:
            for name, value in name_values.items():
                self["parameters"][name] = value
        else:
            self["parameters"] = name_values
        return self

    def add_region_of_interest(self, name):
        """Add a region of interest to the problem.

        Parameters
        ----------
        name : str
            The name of the region to be added.

        Returns
        -------
        ForwardProblem
            The current forward problem.
        """
        if self.region_of_interest is None:
            self["region_of_interest"] = [name]
        else:
            self.region_of_interest.append(name)
        return self

    def add_regions_of_interest(self, names):
        """Add multiple regions of interest to the problem.

        Parameters
        ----------
        name : list[str]
            The names of the regions to be added.

        Returns
        -------
        ForwardProblem
            The current forward problem.
        """
        if self.region_of_interest is None:
            self["region_of_interest"] = []
        for name in names:
            if name not in self.region_of_interest:
                self.region_of_interest.append(name)
        return self

    def set_undersampling_distance(self, undersampling_distance):
        """Set the minimal distance between two solution elements.

        Parameters
        ----------
        undersampling_distance : float
            The minimal distance between two elements the solution is computed
            on.

        Returns
        -------
        ForwardProblem
            The current forward problem.
        """
        self["undersampling_distance"] = undersampling_distance
        return self

    def get_undersampling_elements(self, model, element_types, elements):
        """Get a subset of elements spaced by the undersampling distance.

        Parameters
        ----------
        model : shamo.model.FEModel
            The model.
        element_types : numpy.ndarray
            A one dimensional array containing the types of the elements.
        elements : numpy.ndarray
            A one dimensional array containing the tags of the elements.

        Returns
        -------
        numpy.ndarray
            The coordinates of all the elements.
        numpy.ndarray
            The tags of the elements equally spaced by the undersampling
            distance.
        numpy.ndarray
            The coordinates of the elements equally spaced by the undersampling
            distance.
        """
        all_element_coordinates = self.get_elements_coordinates(
            model, element_types, elements)
        undersampling_elements = None
        undersampling_element_coordinates = None
        if self.undersampling_distance > 0:
            undersampling_elements, undersampling_element_coordinates = \
                self._get_undersampling_elements(elements,
                                                 all_element_coordinates)
        return (all_element_coordinates, undersampling_elements,
                undersampling_element_coordinates)

    def get_elements_coordinates(self, model, element_types, elements):
        """Get the coordinates of the elements.

        Parameters
        ----------
        model : shamo.model.FEModel
            The model.
        element_types : numpy.ndarray
            A one dimensional array containing the types of the elements.
        elements : numpy.ndarray
            A one dimensional array containing the tags of the elements.

        Returns
        -------
        numpy.ndarray
            The coordinates of the elements.
        """
        gmsh.initialize()
        gmsh.open(model.mesh_path)
        element_coordinates = np.empty((element_types.size, 3))
        element_coordinates[:] = np.nan
        for region_of_interest in self.region_of_interest:
            for entity in model.tissues[region_of_interest].volume_entity:
                entity_types, entity_tags = gmsh.model.mesh.getElements(
                    3, entity)[:2]
                for i, element_type in enumerate(entity_types):
                    type_element_indices = np.argwhere(np.isin(elements,
                                                               entity_tags[i])
                                                       ).flatten()
                    type_element_coordinates = \
                        gmsh.model.mesh.getBarycenters(
                            element_type, entity, False,
                            False).reshape((-1, 3))
                    element_coordinates[type_element_indices, :] = \
                        type_element_coordinates
        gmsh.finalize()
        return element_coordinates

    def _get_undersampling_elements(self, all_elements,
                                    all_element_coordinates):
        all_elements = np.copy(all_elements)
        all_element_coordinates = np.copy(all_element_coordinates)
        undersampling_elements = [all_elements[0]]
        undersampling_element_coordinates = [all_element_coordinates[0]]
        while all_elements.size > 0:
            # Compute all distances
            distances = cdist(undersampling_element_coordinates,
                              all_element_coordinates)
            # Remove all elements which are too close
            minimums = distances.min(axis=0)
            indices = np.argwhere(
                minimums < self.undersampling_distance).flatten()
            all_elements = np.delete(all_elements, indices)
            all_element_coordinates = np.delete(all_element_coordinates,
                                                indices, 0)
            distances = np.delete(distances, indices, 1)
            # Set the new current element
            if all_elements.size > 0:
                closest_index = np.argmin(distances[-1])
                undersampling_elements.append(all_elements[closest_index])
                undersampling_element_coordinates.append(
                    all_element_coordinates[closest_index])
        return (np.array(undersampling_elements).flatten(),
                np.array(undersampling_element_coordinates))

    @classmethod
    def undersample_matrix(cls, matrix, n_values_per_element, all_elements,
                           undersampling_elements):
        """Removed unnecessary elements from the matrix.

        Parameters
        ----------
        matrix : numpy.ndarray
            The full matrix.
        n_values_per_element : int
            The number of values per element. For a scalar field 1, vector
            field 3, tensor field 9.
        all_elements : numpy.ndarray
            The tags of all the elements.
        undersampling_elements : numpy.ndarray
            The tags of the elements to keep.

        Returns
        -------
        numpy.ndarray
            The undersampled matrix.
        """
        repeated_elements = np.repeat(all_elements, n_values_per_element)
        indices = np.argwhere(np.isin(repeated_elements,
                                      undersampling_elements, invert=True))
        matrix = np.delete(matrix, indices, axis=1)
        return matrix

    @abc.abstractmethod
    def solve(self, model, name, parent_path, parents=True, exist_ok=True,
              **kwargs):
        """Solve the problem."""
