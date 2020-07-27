"""Implement sensors methods."""
from scipy.spatial.distance import cdist
import numpy as np
import gmsh

from .sensor import Sensor


def add_sensor(self, name, coordinates, on_tissue):
    """Add a sensor to the model.

    Parameters
    ----------
    name : str
        The name of the sensor.
    coordinates : tuple (float, float, float)
        The coordinates of the sensor in the real world [mm].
    on_tissue : str
        The name of the tissue the sensor must be placed on.

    Returns
    -------
    shamo.model.fe_model.FEModel
        The current model.
    """
    # Rescale coordinates [m]
    coordinates = [c / 1000 for c in coordinates]
    # Add sensor
    gmsh.initialize()
    gmsh.open(self.mesh_path)
    node_tags, node_coordinates = _get_tissue_nodes(self, on_tissue)
    distances = cdist([coordinates], node_coordinates).flatten()
    min_distance_index = np.argmin(distances)
    node_tag = node_tags[min_distance_index]
    mesh_coordinates = node_coordinates[min_distance_index, :].flatten()
    entity, group = _add_sensor_on_node(name, node_tag, mesh_coordinates)
    sensor = Sensor(coordinates, mesh_coordinates, group, entity, node_tag, on_tissue)
    if self.sensors is None:
        self["sensors"] = {}
    self["sensors"][name] = sensor
    gmsh.model.mesh.removeDuplicateNodes()
    gmsh.option.setNumber("Mesh.Binary", 1)
    gmsh.write(self.mesh_path)
    gmsh.finalize()
    return self


def add_sensors(self, sensor_coordinates, on_tissue):
    """Add multiple sensors to the model.

    Parameters
    ----------
    sensor_coordinates : dict [str, tuple (float, float, float)]
        A dictionary containing the names of the sensors as keys and their
        respective real coordinates as values.
    on_tissue : str
        The name of the tissue the sensor must be placed on.

    Returns
    -------
    shamo.model.fe_model.FEModel
        The current model.
    """
    # Rescale coordinates [m]
    sensor_coordinates = {
        name: [c / 1000 for c in coordinates]
        for name, coordinates in sensor_coordinates.items()
    }
    # Add sensor
    gmsh.initialize()
    gmsh.open(self.mesh_path)
    node_tags, node_coordinates = _get_tissue_nodes(self, on_tissue)
    coordinates = np.array(list(sensor_coordinates.values()))
    distances = cdist(coordinates, node_coordinates)
    min_distance_indices = np.argmin(distances, axis=1)
    node_tag = node_tags[min_distance_indices]
    mesh_coordinates = node_coordinates[min_distance_indices, :]
    for i, name in enumerate(sensor_coordinates.keys()):
        entity, group = _add_sensor_on_node(name, node_tag[i], mesh_coordinates[i])
        sensor = Sensor(
            coordinates[i], mesh_coordinates[i], group, entity, node_tag[i], on_tissue
        )
        if self.sensors is None:
            self["sensors"] = {}
        self["sensors"][name] = sensor
    gmsh.model.mesh.removeDuplicateNodes()
    gmsh.option.setNumber("Mesh.Binary", 1)
    gmsh.write(self.mesh_path)
    gmsh.finalize()
    return self


def _get_tissue_nodes(self, name):
    """Return the nodes tags and coordinates of a tissue.

    Parameters
    ----------
    name: str
        The name of the tissue.

    Returns
    -------
    numpy.ndarray
        The tags of the nodes.
    numpy.ndarray
        The coordinates of the nodes.

    Raises
    ------
    KeyError
        If the tissue defined by ``name`` is not part of the model.

    Notes
    -----
    This method must be called inside a gmsh context.
    """
    # Check arguments
    if name not in self.tissues:
        raise KeyError(("Model does not contain tissue '{}'.").format(name))
    # Acquire the nodes
    tissue = self.tissues[name]
    node_tags = None
    node_coordinates = None
    for entity in tissue.surface_entity:
        tags, coordinates, _ = gmsh.model.mesh.getNodes(2, entity, True)
        if node_tags is None and node_coordinates is None:
            node_tags = tags
            node_coordinates = coordinates
        else:
            node_tags = np.hstack(node_tags, tags)
            node_coordinates = np.hstack(node_coordinates, coordinates)
    return node_tags, node_coordinates.reshape((-1, 3))


def _add_sensor_on_node(name, node_tag, node_coordinates):
    """Add a sensor to the mesh.

    Parameters
    ----------
    name: str
        The name of the sensor.
    node_tag: int
        The tag of the node the sensor must be added on.
    node_coordinates: numpy.ndarray
        The coordinates of the node the sensor must be added on.

    Returns
    -------
    int
        The entity tag of the created sensor.
    int
        The physical group of the created sensor.

    Notes
    -----
    This method must be called inside a gmsh context.
    """
    groups = [tag for dim, tag in gmsh.model.getPhysicalGroups(-1)]
    max_group = max(groups)
    entity = gmsh.model.addDiscreteEntity(0)
    gmsh.model.mesh.addNodes(0, entity, [node_tag], node_coordinates)
    gmsh.model.mesh.removeDuplicateNodes()
    group = gmsh.model.addPhysicalGroup(0, [entity], max_group + 1)
    gmsh.model.setPhysicalName(0, group, name)
    return entity, group
