"""Implement sources methods."""
import gmsh
import numpy as np

from .sources.fe_source import FESource


def add_sources(self, sources, in_tissue, size=0.1, lc=0.001):
    """Add 3D dipoles to the mesh.

    Parameters
    ----------
    sources : shamo.model.sources.surce.Source
        The sources to simulate.
    in_tissue : str
        The name of the tissue to add the sources in.
    size : float, optinal
        The diameter of the source.
    lc : float
        The characteristical length of the elements on the sources.

    Returns
    -------
    shamo.model.fe_model.FEModel
        The current model.
    """
    # Define points offset
    size = 0.001 * size
    lc = 0.001 * lc
    point_offsets = np.array(
        [
            (-size / 2, 0, 0),
            (size / 2, 0, 0),
            (0, -size / 2, 0),
            (0, size / 2, 0),
            (0, 0, -size / 2),
            (0, 0, size / 2),
        ]
    )
    # Remove original mesh for the tissue
    gmsh.initialize()
    gmsh.open(self.mesh_path)
    gmsh.model.removeEntities([(3, self.tissues[in_tissue].volume_entity[0])])
    gmsh.model.removePhysicalGroups([(3, self.tissues[in_tissue].volume_group)])
    # Add the points
    all_points = []
    for source in sources:
        i_source = len(self.sources)
        points_coordinates = point_offsets + source.coordinates
        points = [gmsh.model.geo.addPoint(*point, lc) for point in points_coordinates]
        group = gmsh.model.addPhysicalGroup(0, points, 1000 + i_source * 6)
        gmsh.model.setPhysicalName(0, group, "source{}".format(i_source))
        groups = [gmsh.model.addPhysicalGroup(0, [point]) for point in points]
        for i_point, point_group in enumerate(groups):
            gmsh.model.setPhysicalName(
                0, point_group, "source{}_{}".format(i_source, i_point)
            )
        point_groups = [
            (groups[0], groups[1]),
            (groups[2], groups[3]),
            (groups[4], groups[5]),
        ]
        self["sources"].append(
            FESource([c * 1000 for c in source.coordinates], size, group, point_groups)
        )
        all_points.extend(points)
    # Remesh
    surface_loop = gmsh.model.geo.addSurfaceLoop(self.tissues[in_tissue].surface_entity)
    volume = gmsh.model.geo.addVolume([surface_loop])
    group = gmsh.model.addPhysicalGroup(
        3, [volume], self.tissues[in_tissue].volume_group
    )
    self.tissues[in_tissue]["volume_entity"] = [volume]
    gmsh.model.setPhysicalName(3, group, in_tissue)
    gmsh.model.geo.synchronize()
    gmsh.model.mesh.embed(0, all_points, 3, volume)
    gmsh.model.mesh.generate(3)
    gmsh.option.setNumber("Mesh.Binary", 1)
    # Update number of nodes
    nodes = gmsh.model.mesh.getNodes(-1, -1, False, False)[0]
    self["n_nodes"] = nodes.size
    gmsh.write(self.mesh_path)
    gmsh.finalize()


def source_exists(self, source):
    """Check if the source is defined in the model.

    Parameters
    ----------
    source : shamo.model.sources.source.Source
        The source.

    Returns
    -------
    bool
        Return ``True`` if the source exists in the model, ``False`` otherwise.
    """
    for model_source in self.sources:
        if source.coordinates == model_source.coordinates:
            return True
    return False


def get_source(self, source):
    """Get the model source corresponding to a given source.

    Parameters
    ----------
    source : shamo.model.sources.source.Source
        The source to retrieve.

    Returns
    -------
    shamo.model.sources.fe_source.FESource
        If the source exists in the model, return the source, ``None``
        otherwise.
    """
    for model_source in self.sources:
        if source.coordinates == model_source.coordinates:
            return model_source
    return None
