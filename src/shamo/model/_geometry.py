"""Implement geometry methods."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pygalmesh as cgal
import meshio as mio
import nibabel as nib
import numpy as np
import gmsh

from .mesh_config import MeshConfig
from .tissue import Tissue

MILLIMETER_AFFINE = np.diag((0.001, 0.001, 0.001, 1))


def mesh_from_labels(self, labels, tissues, affine, mesh_config=MeshConfig()):
    """Generate a ``.msh`` file from a labeled array.

    Parameters
    ----------
    labels : numpy.ndarray
        A labeled array corresponding to a multi-segments image. The array
        must contain integer labels starting from ``0`` (void) without
        skipping a number.
    tissues : list [str]
        An Sequence containing the names of the tissues in the order of the
        labels.
    affine : numpy.ndarray
        The affine matrix of the image.
    mesh_config : shamo.model.mesh_config.MeshConfig, optional
        The configuration for the mesh generation. (The default is
        ``shamo.model.mesh_config.MeshConfig()``).

    Returns
    -------
    shamo.model.fe_model.FEModel
        The current model.

    Raises
    ------
    ValueError
        If one of the parameters are not of the right size.

    Notes
    -----
    If a particular temporary directory must be used (e.g. working on a
    cluster), simply set a environment variable called ``SCRATCH_DIR``.
    """
    # Check the arguments
    labels = labels.astype(np.uint8)
    if labels.ndim != 3:
        raise ValueError("Argument `labels` must be a 3D array.")
    if affine.shape != (4, 4):
        raise ValueError("Argument `affine` must be a 2D 4x4 array.")
    n_tissues = np.max(labels)
    if len(tissues) != n_tissues:
        raise ValueError(
            ("Argument `tissue` must contain {} " "names.").format(n_tissues)
        )
    # Generate the mesh
    scratch_path = os.environ.get("SCRATCH_DIR", None)
    with TemporaryDirectory(dir=scratch_path) as parent_path:
        inr_path = _inr_file_from_labels(parent_path, labels)
        mesh_path = _mesh_from_inr_file(parent_path, inr_path, mesh_config)
        transformed_path = _affine_transform(
            parent_path, mesh_path, np.dot(MILLIMETER_AFFINE, affine)
        )
        msh_path = _finalize_mesh(self, transformed_path, tissues)
        self["mesh_path"] = str(Path(msh_path).relative_to(self.path))
        self["tissues"] = get_tissues_from_mesh(msh_path)
    return self


def mesh_from_nii(self, image_path, tissues, mesh_config=MeshConfig()):
    """Generate a ``.msh`` file from a labeled ``.nii`` image.

    Parameters
    ----------
    image_path : str
        A labeled array corresponding to a multi-segments image. The array
        must contain integer labels starting from ``0`` (void) without
        skipping a number.
    tissues : list [str]
        An Sequence containing the names of the tissues in the order of the
        labels.
    mesh_config : MeshConfig, optional
        The configuration for the mesh generation. (The default is
        ``MeshConfig()``).

    Returns
    -------
    shamo.model.fe_model.FEModel
        The current model.

    See Also
    --------
    mesh_from_labels
        To see how the labels are converted into a mesh.

    Notes
    -----
    If a particular temporary directory must be used (e.g. working on a
    cluster), simply set a environment variable called ``SCRATCH_DIR``.
    """
    image = nib.load(image_path)
    labels = image.get_fdata().astype(np.uint8)
    affine = image.affine
    self.mesh_from_labels(labels, tissues, affine, mesh_config)
    return self


def mesh_from_masks(self, tissue_masks, affine, mesh_config=MeshConfig()):
    """Generate a ``.msh`` file from multiple binary masks.

    Parameters
    ----------
    tissue_masks : dict [str, numpy.ndarray]
        A dictionary containing the names of the tissues as keys and the
        corresponding binary masks as values.
    affine : numpy.ndarray
        The affine matrix of the image.
    mesh_config : shamo.model.mesh_config.MeshConfig, optional
        The configuration for the mesh generation. (The default is
        ``MeshConfig()``).

    Returns
    -------
    shamo.model.fe_model.FEModel
        The current model.

    See Also
    --------
    mesh_from_labels
        To see how the labels are converted into a mesh.

    Notes
    -----
    If a particular temporary directory must be used (e.g. working on a
    cluster), simply set a environment variable called ``SCRATCH_DIR``.
    """
    tissues = list(tissue_masks.keys())
    masks = list(tissue_masks.values())
    labels = np.zeros(masks[0].shape, dtype=np.uint8)
    for label, mask in enumerate(masks):
        labels[mask.astype(np.bool)] = label + 1
    self.mesh_from_labels(labels, tissues, affine, mesh_config)
    return self


def mesh_from_niis(self, tissue_paths, mesh_config=MeshConfig()):
    """Generate a ``.msh`` file from multiple ``.nii`` binary masks.

    Parameters
    ----------
    tissue_paths : dict [str, str]
        A dictionary containing the names of the tissues as keys and the
        paths to the corresponding ``.nii`` images as values.
    mesh_config : shamo.model.mesh_config.MeshConfig, optional
        The configuration for the mesh generation. (The default is
        ``shamo.model.mesh_config.MeshConfig()``).

    Returns
    -------
    shamo.model.fe_modelFEModel
        The current model.

    See Also
    --------
    mesh_from_labels
        To see how the labels are converted into a mesh.

    Notes
    -----
    If a particular temporary directory must be used (e.g. working on a
    cluster), simply set a environment variable called ``SCRATCH_DIR``.
    """
    tissue_masks = {
        tissue: nib.load(path).get_fdata().astype(np.bool)
        for tissue, path in tissue_paths.items()
    }
    image = nib.load(list(tissue_paths.values())[0])
    affine = image.affine
    self.mesh_from_masks(tissue_masks, affine, mesh_config)
    return self


def get_tissues_from_mesh(mesh_path):
    """Extract tissues information from a ``.msh`` file.

    Parameters
    ----------
    mesh_path : str
        The path to the ``.msh`` file.

    Returns
    -------
    dict [str, shamo.model.tissue.Tissue]
        A ``dict`` containing the names of the tissues as keys and the
        corresponding ``shamo.model.tissue.Tissue`` object as values.
    """
    gmsh.initialize()
    gmsh.open(mesh_path)
    tissues_data = {}
    for dim, dimension in [(3, "volume"), (2, "surface")]:
        dim_groups = gmsh.model.getPhysicalGroups(dim)
        for _, group in dim_groups:
            name = gmsh.model.getPhysicalName(dim, group)
            entity = gmsh.model.getEntitiesForPhysicalGroup(dim, group)
            if name in tissues_data:
                tissues_data[name]["{}_group".format(dimension)] = group
                tissues_data[name]["{}_entity".format(dimension)] = entity.tolist()
            else:
                tissues_data[name] = {
                    "{}_group".format(dimension): group,
                    "{}_entity".format(dimension): entity.tolist(),
                }
    gmsh.finalize()
    return {name: Tissue(**data) for name, data in tissues_data.items()}


def _inr_file_from_labels(parent_path, labels, name="model"):
    """Generate a ``.inr`` file from a multilabels array.

    Parameters
    ----------
    parent_path : str
        The path to the directory the ``.inr`` must be created in.
    labels : numpy.ndarray
        A labeled array corresponding to a multi-segments image. The array
        must contain integer labels starting from ``0`` (void) without
        skipping a number.
    name : str, optional
        The name of the file without '.inr'. (The default is 'model').

    Returns
    -------
    str
        The path to the generated ``.inr`` file.

    Raises
    ------
    ValueError
        If ``labels`` is not a 3D array.
    TypeError
        If ``labels`` data type is not ``uint8``.
    """
    # Check the arguments
    if labels.ndim != 3:
        raise ValueError("Argument `labels` must be a 3D array.")
    if labels.dtype != np.uint8:
        raise TypeError("Argument `labels` datatype must be `uint8`.")
    # Generate the file
    bytes_type = "unsigned fixed"
    n_bits = 8
    header = (
        "#INRIMAGE-4#{{\n"
        "XDIM={}\n"
        "YDIM={}\n"
        "ZDIM={}\n"
        "VDIM=1\n"
        "TYPE={}\n"
        "PIXSIZE={} bits\n"
        "CPU=decm\n"
        "VX=1\n"
        "VY=1\n"
        "VZ=1\n"
    ).format(*labels.shape, bytes_type, n_bits)
    header = header + "\n" * (256 - 4 - len(header)) + "##}\n"
    inr_path = str(Path(parent_path) / "{}.inr".format(name))
    with open(inr_path, "wb") as inr_file:
        inr_file.write(header.encode("utf-8"))
        inr_file.write(labels.tobytes(order="F"))
    return str(inr_path)


def _mesh_from_inr_file(parent_path, inr_path, mesh_config, name="model"):
    """Generate a ``.mesh`` file from a ``.inr`` file.

    Parameters
    ----------
    parent_path : str
        The path to the directory the ``.mesh`` must be created in.
    inr_path : str
        The path to the ``.inr`` file.
    mesh_config : shamo.model.mesh_config.MeshConfig
        The configuration for the mesh generation.
    name : str, optional
        The name of the file without '.mesh'. (The default is 'model').

    Returns
    -------
    str
        The path to the generated ``.mesh`` file.
    """
    mesh = cgal.generate_from_inr(inr_path, **mesh_config, verbose=False)
    mesh_path = Path(parent_path) / "{}.mesh".format(name)
    mio.write(str(mesh_path), mesh)
    return str(mesh_path)


def _affine_transform(parent_path, mesh_path, affine, name="model"):
    """Apply an affine transform to a mesh.

    Parameters
    ----------
    parent_path : str
        The path to the directory the resulting ``.msh`` must be created in.
    mesh_path : str
        The path to the ``.mesh`` or ``.msh`` file.
    affine : numpy.ndarray
        The affine matrix to apply.
    name : str, optional
        The name of the file without '.msh'. (The default is 'model').

    Returns
    -------
    str
        The path to the generated ``.msh`` file.
    """
    gmsh.initialize()
    gmsh.open(mesh_path)
    gmsh.plugin.run("NewView")
    axes = ["x", "y", "z"]
    for row in range(3):
        for col in range(3):
            gmsh.plugin.setNumber(
                "Transform", "A{}{}".format(row + 1, col + 1), affine[row, col]
            )
        gmsh.plugin.setNumber("Transform", "T{}".format(axes[row]), affine[row, -1])
    gmsh.plugin.run("Transform")
    gmsh.model.mesh.reclassifyNodes()
    msh_path = Path(parent_path) / "{}.msh".format(name)
    gmsh.option.setNumber("Mesh.Binary", 1)
    gmsh.write(str(msh_path))
    gmsh.finalize()
    return str(msh_path)


def _finalize_mesh(self, origin_path, tissues):
    """Add names to the tissues of the ``.msh`` file.

    Parameters
    ----------
    origin_path : str
        The path to the ``.msh`` file.
    tissues : list [str]
        The names of the tissues.

    Returns
    -------
    str
        The path tot the ``.msh`` file.
    """
    gmsh.initialize()
    gmsh.open(origin_path)
    for label, tissue in enumerate(tissues):
        entity = label + 1
        group = gmsh.model.addPhysicalGroup(3, [entity])
        gmsh.model.setPhysicalName(3, group, tissue)
        group = gmsh.model.addPhysicalGroup(2, [entity])
        gmsh.model.setPhysicalName(2, group, tissue)
    # Get n nodes (Required for problem solving and better extract it once
    # rather than each time we want to solve)
    nodes = gmsh.model.mesh.getNodes(-1, -1, False, False)[0]
    self["n_nodes"] = nodes.size
    msh_path = Path(self.path) / "{}.msh".format(self.name)
    gmsh.option.setNumber("Mesh.Binary", 1)
    gmsh.write(str(msh_path))
    gmsh.finalize()
    return str(msh_path)
