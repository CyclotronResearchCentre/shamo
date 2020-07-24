"""Implement mesh methods."""
import numpy as np
from scipy.spatial.distance import cdist

import gmsh


def get_elements_coordinates(model, regions_of_interest, element_types, element_tags):
    """Get the coordinates of the elements.

    Parameters
    ----------
    model : shamo.model.FEModel
        The model.
    regions_of_interest : list[str]
        The names of the regions to get element coordinates for.
    element_types : numpy.ndarray
        A one dimensional array containing the types of the elements.
    element_tags : numpy.ndarray
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
    for region_of_interest in regions_of_interest:
        for entity in model.tissues[region_of_interest].volume_entity:
            entity_types, entity_tags = gmsh.model.mesh.getElements(3, entity)[:2]
            for i, element_type in enumerate(entity_types):
                type_element_indices = np.argwhere(
                    np.isin(element_tags, entity_tags[i])
                ).flatten()
                type_element_coordinates = gmsh.model.mesh.getBarycenters(
                    element_type, entity, False, False
                ).reshape((-1, 3))
                element_coordinates[type_element_indices, :] = type_element_coordinates
    gmsh.finalize()
    return element_coordinates


def get_tissue_elements(model, name):
    """Get the tags and the coordinates of the elements of a tissue.

    Parameters
    ----------
    model : shamo.FEModel
        The model to extract data from.
    name : str
        The name of the tissue.

    Returns
    -------
    numpy.ndarray
        The tags of the elements
    numpy.ndarray
        The coordinates of the elements.
    """
    gmsh.initialize()
    gmsh.open(model.mesh_path)
    element_type_tags = [
        (entity, *gmsh.model.mesh.getElements(3, entity)[:2])
        for entity in model.tissues[name].volume_entity
    ]
    element_tags = []
    element_coordinates = []
    for entity, types, tags in element_type_tags:
        for i, element_type in enumerate(types):
            element_tags.append(tags[i])
            element_coordinates.append(
                gmsh.model.mesh.getBarycenters(element_type, entity, False, False)
            )
    gmsh.finalize()
    all_tags = np.hstack(element_tags)
    all_coordinates = np.hstack(element_coordinates).reshape((-1, 3))
    return all_tags, all_coordinates


def get_equally_spaced_elements(element_tags, element_coordinates, distance):
    """Extract equally spaced elements.

    Parameters
    ----------
    element_tags : numpy.ndarray
        The tags of the elements.
    element_coordinates : numpy.ndarray
        The coordinates of the elements.
    distance : float
        The distance that elements should be distant from.

    Returns
    -------
    numpy.ndarray
        The tags of the remaining elements.
    numpy.ndarray
        The coordinates of the remaining elements.
    """
    # Set the first element
    tags = [element_tags[0]]
    coordinates = [element_coordinates[0]]
    # Remove unnecessary elements
    all_tags = np.copy(element_tags)
    all_coordinates = np.copy(element_coordinates)
    current_coordinates = element_coordinates[0]
    while all_tags.size > 0:
        # Compute all distances
        distances = cdist([current_coordinates], all_coordinates).flatten()
        # Remove elements that are too close
        indices = np.argwhere(distances < distance).flatten()
        all_tags = np.delete(all_tags, indices)
        all_coordinates = np.delete(all_coordinates, indices, 0)
        distances = np.delete(distances, indices)
        # Set new current coordinates
        if all_tags.size > 0:
            index = np.argmin(distances)
            tags.append(all_tags[index])
            coordinates.append(all_coordinates[index])
            current_coordinates = all_coordinates[index]
    return np.array(tags).flatten(), np.array(coordinates)
