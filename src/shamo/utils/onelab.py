"""API for `shamo.utils.onelab`."""
from contextlib import contextmanager
import logging
from pathlib import Path

import gmsh
import nibabel as nib
import numpy as np
from scipy.spatial.distance import cdist

from .logging import stream_to_logger

LOG_PATTERN = "((?P<level>[\w]*)|(?P<percentage>[ \d]{3}%)) +: (?P<text>.*)"


@contextmanager
def gmsh_open(mesh_path, logger=None):
    """A context manager where Gmsh is initialized and its output is piped.

    Parameters
    ----------
    mesh_path :
        The path to the mesh file to open.
    logger : logging.Logger, optional
        The logger to use. (The default is ``None``)
    """
    with stream_to_logger(logger, pattern=LOG_PATTERN):
        gmsh.initialize()
        gmsh.option.setNumber("General.Verbosity", 5)
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.open(str(Path(mesh_path)))
        try:
            yield gmsh
        finally:
            gmsh.finalize()


def read_vector_file(path):
    """Read a table formatted vector field from GetDP.

    Parameters
    ----------
    path : str, byte or os.PathLike
        The path to the output file.

    Returns
    -------
    int
        The data type.
    np.ndarray
        The element tags.
    np.ndarray
        The values.
    """
    data = np.loadtxt(
        Path(path),
        dtype={
            "names": ("type", "tag", "x", "y", "z"),
            "formats": (np.uint8, np.uint, np.float, np.float, np.float),
        },
        usecols=(0, 1, -3, -2, -1),
    )
    return (
        np.unique(data["type"])[0],
        data["tag"],
        np.vstack((data["x"], data["y"], data["z"])).T,
    )


def get_elems_coords(elem_type, elems_tags):
    """Get the coordinates of specified elements.

    Parameters
    ----------
    elem_type : int
        The type of the elements in `elem_tags`.
    elems_tags : numpy.ndarray
        The tags of the elements to acquire the coordinates for.

    Returns
    -------
    numpy.ndarray
        The coordinates of the specified elements.

    Notes
    -----
    This method must be called inside a Gmsh context.
    """
    coords = []
    tags = []
    coords = gmsh.model.mesh.getBarycenters(elem_type, -1, False, False)
    coords = coords.reshape((-1, 3))
    tags = gmsh.model.mesh.getElementsByType(elem_type, -1)[0]
    idx = np.argsort(tags)
    tags = tags[idx]
    coords = coords[idx, :]
    idx = elems_tags - tags[0]
    coords = coords[idx, :]
    return coords


def get_elems_subset(dim, tags, min_dist):
    """Get a subset of elements based on a minimal distance between them.

    Parameters
    ----------
    dim : int
        The dimension of the elements.
    tags : list [int]
        The entity tags.
    min_dist : float
        The minimal distance between elements.

    Returns
    -------
    numpy.ndarray
        The elements tags.
    numpy.ndarray
        The elements coordinates.
    """
    elems_tags = []
    for t in tags:
        elems_type, ts, _ = gmsh.model.mesh.getElements(dim, t)
        elems_tags.append(ts)
    elems_tags = np.hstack(elems_tags)
    elems_type = elems_type[0]
    elems_tags = elems_tags[0]
    coords = get_elems_coords(elems_type, elems_tags)
    sub_elems_tags = [elems_tags[0]]
    sub_elems_coords = [coords[0]]
    while elems_tags.size > 0:
        dist = cdist([sub_elems_coords[-1]], coords)[0]
        idx = dist < min_dist
        elems_tags = np.delete(elems_tags, idx)
        coords = np.delete(coords, idx, axis=0)
        dist = np.delete(dist, idx)
        if elems_tags.size > 0:
            idx = np.argmin(dist)
            sub_elems_tags.append(elems_tags[idx])
            sub_elems_coords.append(coords[idx])
    return sub_elems_tags, sub_elems_coords


def pos_to_nii(src, dst, affine, shape, mask=None):
    """Convert a POS file into a NII file.

    Parameters
    ----------
    src : str, byte or os.PathLike
        The path to the input NII file.
    dst : str, byte or os.PathLike
        The path to the output NII file.
    affine : numpy.ndarray
        The affine matrix of the NII volume.
    shape : Iterable [float]
        The shape of the NII volume.
    mask : numpy.ndarray, optional
        If not set to ``None``, the mask is applied to the field.

    Returns
    -------
    nibabel.Nifti1Image
        The generated NII image.
    """
    # Define axis
    o = affine @ np.array([-0.5, -0.5, -0.5, 1]).T
    u = affine @ np.array([shape[0] - 0.5, -0.5, -0.5, 1]).T
    v = affine @ np.array([-0.5, shape[1] - 0.5, -0.5, 1]).T
    w = affine @ np.array([-0.5, -0.5, shape[2] - 0.5, 1]).T
    with gmsh_open(src) as gmsh:
        gmsh.option.setNumber("Mesh.Binary", 1)
        # Set plugin parameters
        gmsh.plugin.setNumber("CutBox", "X0", o[0])
        gmsh.plugin.setNumber("CutBox", "Y0", o[1])
        gmsh.plugin.setNumber("CutBox", "Z0", o[2])
        gmsh.plugin.setNumber("CutBox", "X1", u[0])
        gmsh.plugin.setNumber("CutBox", "Y1", u[1])
        gmsh.plugin.setNumber("CutBox", "Z1", u[2])
        gmsh.plugin.setNumber("CutBox", "X2", v[0])
        gmsh.plugin.setNumber("CutBox", "Y2", v[1])
        gmsh.plugin.setNumber("CutBox", "Z2", v[2])
        gmsh.plugin.setNumber("CutBox", "X3", w[0])
        gmsh.plugin.setNumber("CutBox", "Y3", w[1])
        gmsh.plugin.setNumber("CutBox", "Z3", w[2])
        gmsh.plugin.setNumber("CutBox", "Boundary", 0)
        gmsh.plugin.setNumber("CutBox", "NumPointsU", shape[0] + 1)
        gmsh.plugin.setNumber("CutBox", "NumPointsV", shape[1] + 1)
        gmsh.plugin.setNumber("CutBox", "NumPointsW", shape[2] + 1)
        # Run plugin
        gmsh.plugin.run("CutBox")
        # Get field data
        dtype, n_elems, data = gmsh.view.getListData(1)
        gmsh.view.write(1, str(Path(dst).parent / f"{Path(dst).stem}_grid.pos"))
    n_elems = n_elems[0]
    data = data[0]
    data = data.reshape((n_elems, -1))
    n_vals = int(data[:, 24:].shape[1] / 8)
    vals = np.zeros((n_elems, n_vals))
    for i in range(n_vals):
        vals[:, i] = np.mean(data[:, 24 + i :: n_vals], axis=1)
    field = vals.reshape((*shape, n_vals))
    if mask is not None:
        field[~mask, ...] = 0
    # Write NII file
    img = nib.Nifti1Image(field, affine)
    img.to_filename(Path(dst))
    return img
