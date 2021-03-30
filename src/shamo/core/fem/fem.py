"""Implement the `FEM` class."""
from collections.abc import Mapping, Iterable
import copy
from functools import partialmethod
import logging
from pathlib import Path
from pprint import pformat
from tempfile import TemporaryDirectory

import gmsh
import meshio
import nibabel as nib
from nilearn.image import crop_img
import numpy as np
import pygalmesh as cgal
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial.distance import cdist

from shamo.core.objects import ObjDir
from . import Field, Group, Tissue, SensorABC, PointSensor, CircleSensor
from shamo.utils.onelab import gmsh_open

logger = logging.getLogger(__name__)


class FEM(ObjDir):
    """A finite element model.

    Parameters
    ----------
    name : str
        The name of the model.
    parent_path : str, byte or os.PathLike
        The path to the parent directory of the model.
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path)
        self.update(
            {
                "tissues": {
                    t: Tissue(**d) for t, d in kwargs.get("tissues", {}).items()
                },
                "mesh_params": kwargs.get("mesh_params", {}),
                "sensors": {
                    s: SensorABC.load(**d) for s, d in kwargs.get("sensors", {}).items()
                },
            }
        )
        logger.info(f"Model '{name}' initialized in '{parent_path}'  directory.")

    @property
    def nii_path(self):
        """Return the path to the NIFTI file.

        Returns
        -------
        pathlib.Path
            The path to the NIFTI file.
        """
        return self.path / f"{self.name}.nii"

    @property
    def affine(self):
        """Return the affine matrix of the NIFTI file.

        Returns
        -------
        numpy.ndarray
            The affine matrix of the NIFTI file.
        """
        img = nib.load(self.nii_path)
        return img.affine

    @property
    def shape(self):
        """Return the shape of the NIFTI file.

        Returns
        -------
        numpy.ndarray
            The shape of the NIFTI file.
        """
        img = nib.load(self.nii_path)
        return img.shape

    @property
    def mesh_path(self):
        """Return the path to the MSH file.

        Returns
        -------
        pathlib.Path
            The path to the MSH file.
        """
        return self.path / f"{self.name}.msh"

    @property
    def tissues(self):
        """Return the tissues of the model.

        Returns
        -------
        dict [str, shamo.fem.Tissue]
            The tissues of the model.
        """
        return self["tissues"]

    @property
    def sensors(self):
        """Return the sensors of the model.

        Returns
        -------
        dict [str, shamo.fem.SensorABC]
            The sensors of the model.
        """
        return self["sensors"]

    @property
    def mesh_params(self):
        """Return the parameters used to produce the mesh.

        Returns
        -------
        dict [str, float]
            The parameters used to produce the mesh.
        """
        return self["mesh_params"]

    # Mesh -----------------------------------------------------------------------------

    def mesh_from_array(self, labels, affine, tissues, **kwargs):
        """Generate a MSH file from a labelled array.

        Parameters
        ----------
        labels : numpy.ndarray
            A labelled array corresponding to a multi-segments image. The array must
            contain int labels starting from ``0`` (air) without skipping a number.
        affine : numpy.ndarray
            The affine matrix of the volume.
        tissues : iterable [str]
            The names of the tissues in the same order as the labels.

        Other Parameters
        ----------------
        lloyd : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        odt : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        perturb : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        exude : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_edge_size_at_feature_edges: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        min_facet_angle: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_radius_surface_delaunay_ball: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_cell_circumradius: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_facet_distance: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_circumradius_edge_ratio: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        seed : int, optional
            For more information, refer to the documentation of `pygalmesh`.

        Raises
        ------
        TypeError
            If argument 'labels' is not a `numpy.ndarray`.
            If argument 'affine' is not a `numpy.ndarray`.
            If an element of argument 'tissues' is not a `str`.
        ValueError
            If argument 'labels' is not a 3D array.
            If argument 'affine' is neither a (3, 4) nor a (4, 4) array.
            If argument 'tissues' does not contain as many elements as there are labels
            in 'labels'.

        See Also
        --------
        pygalmesh.generate_from_array
        """
        if not isinstance(labels, np.ndarray):
            raise TypeError("Argument 'labels' expects type numpy.ndarray.")
        labels = labels.astype(np.uint8)
        if labels.ndim != 3:
            raise ValueError("Argument 'labels' must be a 3D array.")
        if not isinstance(affine, np.ndarray):
            raise TypeError("Argument 'affine' expects type numpy.ndarray.")
        if affine.shape not in ((3, 4), (4, 4)):
            raise ValueError("Argument 'affine' expects shape (3,4) or (4,4).")
        affine = np.vstack((affine[:3, :], np.array([0, 0, 0, 1])))
        # Convert [mm] to [m]
        affine = np.diag([1e-3] * 3 + [1]) @ affine
        tissues = list(tissues)
        for t in tissues:
            if not isinstance(t, str):
                raise TypeError("Argument 'tissues' expects an iterable of str.")
        if len(tissues) != np.max(labels):
            raise ValueError(
                (
                    "Argument 'tissues' must contain as many names "
                    "as there are unique labels in 'labels'."
                )
            )

        img = nib.Nifti1Image(labels, affine)
        cropped_img = crop_img(img)
        cropped_img.to_filename(self.nii_path)
        labels = cropped_img.get_fdata().astype(np.uint16)
        affine = cropped_img.affine

        with TemporaryDirectory() as d:
            self._gen_init_mesh(labels, np.eye(4), d, **kwargs)
            self._apply_transform(affine, d)
            self._add_tissues(tissues, d)
        self.save()
        logger.info("Mesh generated.")

    def mesh_from_nii(self, nii_path, tissues, **kwargs):
        """Generate a MSH file from a labelled NIFTI file.

        Parameters
        ----------
        nii_path : str, byte or os.PathLike
            The path to the NIFTI file containing the labelled volume.
        tissues : iterable [str]
            The names of the tissues in the same order as the labels.

        Other Parameters
        ----------------
        lloyd : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        odt : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        perturb : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        exude : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_edge_size_at_feature_edges: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        min_facet_angle: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_radius_surface_delaunay_ball: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_cell_circumradius: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_facet_distance: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_circumradius_edge_ratio: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        seed : int, optional
            For more information, refer to the documentation of `pygalmesh`.

        Raises
        ------
        TypeError
            If argument `nii_path` is not a `str`, `byte` or `os.PathLike`.

        See Also
        --------
        FEM.mesh_from_array
        pygalmesh.generate_from_array
        """
        nii_path = Path(nii_path)

        img = nib.load(str(nii_path))
        return self.mesh_from_array(
            img.get_fdata().astype(np.uint8), img.affine, tissues, **kwargs
        )

    def mesh_from_masks(self, masks, affine, **kwargs):
        """Generate a MSH file from multiple binary masks.

        Parameters
        ----------
        mask : Mapping [str, numpy.ndarray]
            A mapping from the names of the tissues to the corresponding binary masks.
        affine : numpy.ndarray
            The affine matrix of the volume.

        Other Parameters
        ----------------
        lloyd : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        odt : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        perturb : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        exude : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_edge_size_at_feature_edges: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        min_facet_angle: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_radius_surface_delaunay_ball: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_cell_circumradius: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_facet_distance: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_circumradius_edge_ratio: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        seed : int, optional
            For more information, refer to the documentation of `pygalmesh`.

        Raises
        ------
        TypeError
            If argument `masks` is not a mapping from `str` to `numpy.ndarray`.
        ValueError
            If the masks in 'masks' are not all of the same shape.

        See Also
        --------
        FEM.mesh_from_array
        pygalmesh.generate_from_array
        """
        if not isinstance(masks, Mapping):
            raise TypeError(
                "Argument 'masks' expects a mapping from str to numpy.ndarray."
            )
        for t in masks.keys():
            if not isinstance(t, str):
                raise TypeError(
                    "Argument 'masks' expects a mapping from str to numpy.ndarray."
                )
        shape = None
        for m in masks.values():
            if not isinstance(m, np.ndarray):
                raise TypeError(
                    "Argument 'masks' expects a mapping from str to numpy.ndarray."
                )
            if shape is not None and m.shape != shape:
                raise ValueError(
                    "Values in argument 'masks' must all have the same shape."
                )
            shape = m.shape

        labels = np.zeros(list(masks.values())[0].shape)
        tissues = []
        for l, (t, m) in enumerate(masks.items()):
            labels[m.astype(bool)] = l + 1
            tissues.append(t)
        return self.mesh_from_array(labels, affine, tissues, **kwargs)

    def mesh_from_niis(self, niis, **kwargs):
        """Generate a MSH file from multiple binary masks.

        Parameters
        ----------
        niis : Mapping [str, str, byte or os.PathLike]
            A mapping from the names of the tissues to the path to the corresponding
            NIFTI binary masks.

        Other Parameters
        ----------------
        lloyd : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        odt : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        perturb : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        exude : bool, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_edge_size_at_feature_edges: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        min_facet_angle: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_radius_surface_delaunay_ball: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_cell_circumradius: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_facet_distance: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        max_circumradius_edge_ratio: float, optional
            For more information, refer to the documentation of `pygalmesh`.
        seed : int, optional
            For more information, refer to the documentation of `pygalmesh`.

        Raises
        ------
        TypeError
            If argument `niis` is not a mapping from `str` to `str`, `byte` or
            `os.PathLike`.

        See Also
        --------
        FEM.mesh_from_masks
        FEM.mesh_from_array
        pygalmesh.generate_from_array
        """
        if not isinstance(niis, Mapping):
            raise TypeError(
                (
                    "Argument 'niis' expects a mapping from str "
                    "to str, byte or os.PathLike."
                )
            )
        for t, p in niis.items():
            niis[t] = Path(p)

        imgs = {t: nib.load(str(p)) for t, p in niis.items()}
        return self.mesh_from_masks(
            {t: i.get_fdata() for t, i in imgs.items()},
            list(imgs.values())[0].affine,
            **kwargs,
        )

    def _gen_init_mesh(self, labels, affine, tmp_dir, **kwargs):
        """Generate the initial mesh usign CGAL."""
        init_mesh = cgal.generate_from_array(
            labels, nib.affines.voxel_sizes(affine), **kwargs
        )
        meshio.write(str(Path(tmp_dir) / "init_mesh.mesh"), init_mesh)
        self["mesh_params"] = kwargs
        logger.info("Initial mesh generated.")

    def _apply_transform(self, affine, tmp_dir):
        """Apply the affine transform to the mesh."""
        with gmsh_open(Path(tmp_dir) / "init_mesh.mesh", logger) as gmsh:
            gmsh.plugin.run("NewView")
            axes = ["x", "y", "z"]
            for r in range(3):
                for c in range(3):
                    gmsh.plugin.setNumber(
                        "Transform", "A{}{}".format(r + 1, c + 1), affine[r, c]
                    )
                gmsh.plugin.setNumber("Transform", "T{}".format(axes[r]), affine[r, -1])
            gmsh.plugin.run("Transform")
            # gmsh.model.mesh.reclassifyNodes()
            gmsh.option.setNumber("Mesh.Binary", 1)
            gmsh.write(str(Path(tmp_dir) / "init_mesh.msh"))
        logger.info("Affine transformation applied.")

    def _add_tissues(self, tissues, tmp_dir):
        """Add the tissues as physical groups."""
        with gmsh_open(Path(tmp_dir) / "init_mesh.msh", logger) as gmsh:
            for l, t in enumerate(tissues):
                entity = l + 1
                surf_group = gmsh.model.addPhysicalGroup(2, [entity])
                gmsh.model.setPhysicalName(2, surf_group, t)
                vol_group = gmsh.model.addPhysicalGroup(3, [entity])
                gmsh.model.setPhysicalName(3, vol_group, t)
                self["tissues"][t] = Tissue(
                    Group(2, [entity], surf_group), Group(3, [entity], vol_group)
                )
                logger.info(f"Tissue '{t}' added.")
            gmsh.option.setNumber("Mesh.Binary", 1)
            gmsh.write(str(self.mesh_path))

    def mesh_from_fem(self, fem_path, merges):
        """Generate a mesh from an existing FEM by merging tissues.

        Parameters
        ----------
        fem_path : str, byte or os.PathLike
            The path to the original model.
        merges : dict [str, list [str]]
            The merges to perform. Each value contains the names of the tissues to merge
            into a tissue named with the key.

        Notes
        -----
        This method removes the fields contained in the tissues that are part of a merge
        and edit the tissue the sensors are placed in/on.
        """
        fem = FEM.load(fem_path)
        with gmsh_open(fem.mesh_path, logger) as gmsh:
            for merge_to, merge_from in merges.items():
                self._merge_tissues(fem, merge_from, merge_to)
            gmsh.write(str(self.mesh_path))
        self["tissues"] = fem.tissues
        self["sensors"] = fem.sensors
        self.save()
        logger.info("Mesh generated.")

    def _merge_tissues(self, fem, merge_from, merge_to):
        """Merge multiple tissues into one."""
        # Edit mesh
        surf_entities = []
        vol_entities = []
        for t in merge_from:
            surf_entities.extend(fem.tissues[t].surf.entities)
            vol_entities.extend(fem.tissues[t].surf.entities)
        max_tag = np.max([t for _, t in gmsh.model.getPhysicalGroups(-1)])
        surf_group = gmsh.model.addPhysicalGroup(2, surf_entities, max_tag + 1)
        vol_group = gmsh.model.addPhysicalGroup(3, vol_entities, max_tag + 2)
        for t in merge_from:
            gmsh.model.removePhysicalGroups(
                [(2, fem.tissues[t].surf.group), (3, fem.tissues[t].vol.group)]
            )
            for f in fem.tissues[t].fields.values():
                gmsh.view.remove(f.view)
            fem.tissues.pop(t, None)
        gmsh.model.setPhysicalName(2, surf_group, merge_to)
        gmsh.model.setPhysicalName(3, vol_group, merge_to)
        # Edit model tissues
        fem["tissues"][merge_to] = Tissue(
            Group(2, surf_entities, surf_group), Group(3, vol_entities, vol_group)
        )
        # Edit model sensors
        for s in fem.sensors.values():
            if s.tissue in merge_from:
                s["tissue"] = merge_to
        logger.info(f"Merged {len(merge_from)} tissues into {merge_to}.")

    def mesh_from_surfaces(self, tissues, structure, lc=0.0):
        """Generate a mesh from a series of surface meshes.

        Parameters
        ----------
        tissues : dict [str, str | byte | os.PathLike]
            A dictionary containing the names of the tissues as keys and the path
            leading to the corresponding surface mesh as values.
        structure : list [str | list]
            A tree structure defined as a nested list defining the way surfaces contain
            each other.
        lc : float | dict [str, float], optional
            The characteristic length of the mesh elements. If set to ``0``, it is
            infered from the size of the surface elements. If a float value is used, the
            same size is set for the whole volume. If a dictionary is provided, it must
            contain the name of the tissues (or default) as keys and the corresponding
            characteristic length as values. (The default is ``0.0``)

        Raises
        ------
        ValueError
            If argument `lc` is a dictionary, does not contain all the tissues and have
            no ``default`` key.
        """
        with TemporaryDirectory() as d:
            oredered_tissues = self._gen_mesh_from_surfaces(tissues, structure, lc, d)
            self._add_tissues(oredered_tissues, d)
        self.save()
        logger.info("Mesh generated.")

    def _gen_mesh_from_surfaces(self, tissues, structure, lc, tmp_dir):
        """Generate the initial mesh from a series of surfaces."""
        indices = {}
        oredered_tissues = []
        with gmsh_open(str(Path(tmp_dir) / "init_mesh.msh"), logger) as gmsh:
            # Add the surfaces
            for i, (t, p) in enumerate(tissues.items()):
                gmsh.merge(str(Path(p)))
                gmsh.model.geo.addSurfaceLoop([i + 1])
                indices[t] = i + 1
                oredered_tissues.append(t)
            # Add the volumes
            for t, v in self._get_surf_loops(structure).items():
                gmsh.model.geo.addVolume([indices[n] for n in v], indices[t])
            gmsh.model.geo.synchronize()
            gmsh.option.setNumber("Mesh.Binary", 1)
            if isinstance(lc, float):
                # Constant lc accross the whole mesh (or 0)
                if lc != 0.0:
                    gmsh.option.setNumber(
                        "Mesh.CharacteristicLengthExtendFromBoundary", 0
                    )
                    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc)
                gmsh.model.mesh.generate(3)
                gmsh.write(str(Path(tmp_dir) / "init_mesh.msh"))
                logger.info("Initial mesh generated.")
                return oredered_tissues
            # Generate a coarse mesh
            if "default" not in lc:
                for t in oredered_tissues:
                    if t not in lc:
                        raise ValueError(
                            "Argument 'lc' must contain all the tissues or a 'default' key."
                        )
                lc["default"] = 0.0
            gmsh.option.setNumber("Mesh.CharacteristicLengthExtendFromBoundary", 0)
            restricts = []
            for t in oredered_tissues:
                box = gmsh.model.mesh.field.add("Box")
                gmsh.model.mesh.field.setNumber(box, "VIn", lc.get(t, lc["default"]))
                s = 1
                for a in ("X", "Y", "Z"):
                    for b in ("Max", "Min"):
                        gmsh.model.mesh.field.setNumber(box, f"{a}{b}", s * 999999.9)
                        s *= -1
                restrict = gmsh.model.mesh.field.add("Restrict")
                gmsh.model.mesh.field.setNumber(restrict, "InField", box)
                gmsh.model.mesh.field.setNumbers(restrict, "VolumesList", [indices[t]])
                restricts.append(restrict)
            # Min because Restrict returns 1e22 outside
            mesh_size = gmsh.model.mesh.field.add("Min")
            gmsh.model.mesh.field.setNumbers(mesh_size, "FieldsList", restricts)
            gmsh.model.mesh.field.setAsBackgroundMesh(mesh_size)
            gmsh.model.mesh.generate(3)
            gmsh.write(str(Path(tmp_dir) / "init_mesh.msh"))
        logger.info("Initial mesh generated.")
        return oredered_tissues

    def _get_surf_loops(self, structure):
        """Extract surface loops booleans from tree structure."""
        vols = {}
        queue = []
        while structure:
            first = structure.pop(0)
            current = None
            children = []
            if isinstance(first, str):
                current = first
                if structure:
                    children = [
                        s[0] if len(structure[0]) > 1 else s for s in structure[0]
                    ]
                vols[current] = [current, *children]
            elif isinstance(first, list):
                queue.append(first)
            if not structure and queue:
                structure = queue.pop(0)
        return vols

    # Sensors --------------------------------------------------------------------------

    def add_point_sensor(self, name, coords, tissue, dim):
        """Add a point sensor to the mesh.

        Parameters
        ----------
        name : str
            The name of the sensor.
        coords : Iterable [float] or numpy.ndarray
            The coordinates of the sensor.
        tissue : str
            The name of the tissue the sensor is on/in.
        dim : int
            If set to ``2``, the sensor is added on the surface of the tissue. If set to
            ``3``, it is placed inside the tissue.

        Raises
        ------
        TypeError
            If argument `coords` is neither an `Iterable` or a `numpy.ndarray`.
            If argument `dim` is not an `int`.
        ValueError
            If argument `name` refers to an existing sensor.
            If argument `coords` is not a proper 3D coordinate.
            If argument `tissue` refers to a non existing tissue.
        """
        if name in self.sensors:
            raise ValueError(f"Sensor '{name}' already exists in model.")
        if not isinstance(coords, (Iterable, np.ndarray)):
            raise TypeError("Argument 'coords' expects type Iterable or numpy.ndarray.")
        if len(coords) != 3:
            raise ValueError("Argument 'coords' must be a 3D coordinate.")
        coords = tuple([1e-3 * c for c in coords])
        if tissue not in self.tissues:
            raise ValueError(f"Tissue '{tissue}' not found in model.")
        dim = int(dim)

        logger.debug(
            (
                f"Adding 1 sensor {'on' if dim == 2 else 'in'} "
                f"tissue '{tissue}' with coords:\n{coords}"
            )
        )
        with gmsh_open(self.mesh_path, logger) as gmsh:
            nodes_tags, nodes_coords = self._get_tissue_nodes(tissue, dim)
            self._add_point_sensor(name, coords, nodes_tags, nodes_coords, tissue)
            gmsh.model.mesh.removeDuplicateNodes()
            gmsh.option.setNumber("Mesh.Binary", 1)
            gmsh.write(str(self.mesh_path))
        self.save()
        logger.info(f"Sensor '{name}' added.")

    add_point_sensor_on = partialmethod(add_point_sensor, dim=2)
    add_point_sensor_in = partialmethod(add_point_sensor, dim=3)

    def add_point_sensors(self, coords, tissue, dim):
        """Add multiple point sensors to the mesh.

        Parameters
        ----------
        coords : Mapping [str, Iterable [float]]
            The coordinates of the sensor.
        tissue : str
            The name of the tissue the sensor is on/in.
        dim : int
            If set to ``2``, the sensor is added on the surface of the tissue. If set to
            ``3``, it is placed inside the tissue.

        Raises
        ------
        TypeError
            If argument `coords` is not a Mapping of coordinates.
            If argument `dim` is not an `int`.
        ValueError
            If argument `tissue` refers to a non existing tissue.
        """
        coords = {s: tuple([1e-3 * x for x in c]) for s, c in coords.items()}
        if tissue not in self.tissues:
            raise ValueError(f"Tissue '{tissue}' not found in model.")
        dim = int(dim)

        logger.debug(
            (
                f"Adding {len(coords)} sensors {'on' if dim == 2 else 'in'} "
                f"tissue '{tissue}' with coords:\n{pformat(coords)}"
            )
        )
        with gmsh_open(self.mesh_path, logger) as gmsh:
            nodes_tags, nodes_coords = self._get_tissue_nodes(tissue, dim)
            for s, c in coords.items():
                self._add_point_sensor(s, c, nodes_tags, nodes_coords, tissue)
                logger.info(
                    f"Sensor '{s}' added {'on' if dim == 2 else 'in'} tissue '{tissue}'."
                )
            gmsh.model.mesh.removeDuplicateNodes()
            gmsh.option.setNumber("Mesh.Binary", 1)
            gmsh.write(str(self.mesh_path))
        self.save()

    add_point_sensors_on = partialmethod(add_point_sensors, dim=2)
    add_point_sensors_in = partialmethod(add_point_sensors, dim=3)

    def add_point_sensors_from_tsv(self, tsv_path, tissue, dim):
        """Add multiple point sensors to the mesh from a TSV file.

        Parameters
        ----------
        tsv_path : str, byte or os.PathLike
            The path to the TSV file.
        tissue : str
            The name of the tissue the sensor is on/in.
        dim : int
            If set to ``2``, the sensor is added on the surface of the tissue. If set to
            ``3``, it is placed inside the tissue.

        Raises
        ------
        TypeError
            If argument `coords` is not a Mapping of coordinates.
            If argument `dim` is not an `int`.
        ValueError
            If argument `tissue` refers to a non existing tissue.
        """
        tsv_path = Path(tsv_path)
        data = np.genfromtxt(
            tsv_path, delimiter="\t", skip_header=1, dtype=None, encoding="utf-8"
        )
        coords = {d[0]: [d[1], d[2], d[3]] for d in data}
        logger.info(f"{len(coords)} sensors coordinates extracted from '{tsv_path}'.")
        logger.debug(pformat(coords))
        return self.add_point_sensors(coords, tissue, dim)

    add_point_sensors_from_tsv_on = partialmethod(add_point_sensors_from_tsv, dim=2)
    add_point_sensors_from_tsv_in = partialmethod(add_point_sensors_from_tsv, dim=3)

    def add_circle_sensor_on(self, name, coords, tissue, radius):
        """Add a circle sensor on a surface.

        Parameters
        ----------
        name : str
            The name of the sensor.
        coords : tuple [float, float, float]
            The coordinates of the sensor in the subject space.
        tissue : str
            The name of the tissue the sensor must be added on.
        radius : float
            The radius of the sensor [m].

        Raises
        ------
        ValueError
            If a sensor with name `name` already exists.
            If the coordinates are not a 3D location.
            If the tissue `tissue` does not exist in the model.
        TypeError
            If the argument `coords` is not of the right type.
        """
        if name in self.sensors:
            raise ValueError(f"Sensor '{name}' already exists in model.")
        if not isinstance(coords, (Iterable, np.ndarray)):
            raise TypeError("Argument 'coords' expects type Iterable or numpy.ndarray.")
        if len(coords) != 3:
            raise ValueError("Argument 'coords' must be a 3D coordinate.")
        coords = tuple([1e-3 * c for c in coords])
        if tissue not in self.tissues:
            raise ValueError(f"Tissue '{tissue}' not found in model.")

        # WARNING: Only works with triangles, with single entity physical surfaces.
        surf = self.tissues[tissue].surf
        with gmsh_open(self.mesh_path, logger) as gmsh:
            nodes_tags, nodes_coords = self._get_tissue_nodes(tissue, 2)
            # Get closest node
            dist = cdist([coords], nodes_coords).ravel()
            min_dist_idx = np.argmin(dist)
            node_tag = nodes_tags[min_dist_idx]
            mesh_coords = nodes_coords[min_dist_idx, :]
            # Get surface elements
            elems_type, elems_tags, elems_nodes_tags = gmsh.model.mesh.getElements(
                2, surf.entities[0]
            )
            elems_type = elems_type[0]
            elems_tags = elems_tags[0]
            elems_nodes_tags = elems_nodes_tags[0].reshape((-1, 3))
            elems_coords = gmsh.model.mesh.getBarycenters(
                elems_type, surf.entities[0], False, False
            ).reshape((-1, 3))
            # Keep only elements in radius
            dist = cdist([mesh_coords], elems_coords).ravel()
            mask = dist <= radius
            valid_elems_tags = elems_tags[mask]
            valid_elems_nodes_tags = elems_nodes_tags[mask, :].ravel()
            # Only keep elements directly connected to closest node
            valid_elems_repeated = valid_elems_tags.repeat((3,))
            nodes_to_check = [node_tag]
            elems = []
            nodes = []
            while nodes_to_check:
                current = nodes_to_check.pop(0)
                nodes.append(current)
                mask = valid_elems_nodes_tags == current
                connected_elems = valid_elems_repeated[mask]
                for e_t in connected_elems:
                    elems.append(e_t)
                    mask = valid_elems_repeated == e_t
                    connected_nodes = valid_elems_nodes_tags[mask]
                    for n_t in connected_nodes:
                        if n_t not in nodes and n_t not in nodes_to_check:
                            nodes_to_check.append(n_t)
                    valid_elems_repeated = np.delete(valid_elems_repeated, mask)
                    valid_elems_nodes_tags = np.delete(valid_elems_nodes_tags, mask)
            mask = np.in1d(elems_tags, elems, assume_unique=True)
            valid_elems_tags = elems_tags[mask]
            valid_elems_nodes_tags = elems_nodes_tags[mask, :].ravel()
            # Add surface sensor
            surf_entity = gmsh.model.addDiscreteEntity(2)
            gmsh.model.mesh.addElements(
                2,
                surf_entity,
                [elems_type],
                [valid_elems_tags],
                [valid_elems_nodes_tags],
            )
            max_group = np.max([t for d, t in gmsh.model.getPhysicalGroups()])
            surf_group = gmsh.model.addPhysicalGroup(2, [surf_entity], max_group + 1)
            gmsh.model.setPhysicalName(2, surf_group, name)
            # Remove elements from the tissue
            new_entity = gmsh.model.addDiscreteEntity(2)
            gmsh.model.mesh.addElements(
                2,
                new_entity,
                [elems_type],
                [elems_tags[~mask]],
                [elems_nodes_tags[~mask, :].ravel()],
            )
            gmsh.model.removeEntities([(2, surf.entities[0])])
            try:
                gmsh.model.removePhysicalGroups([(2, surf.group)])
            except:
                pass
            gmsh.model.removePhysicalName(tissue)
            g = gmsh.model.addPhysicalGroup(2, [new_entity], surf.group)
            gmsh.model.setPhysicalName(2, surf.group, tissue)
            gmsh.model.setPhysicalName(3, self.tissues[tissue].vol.group, tissue)
            gmsh.model.mesh.removeDuplicateNodes()
            gmsh.model.mesh.reclassifyNodes()
            gmsh.option.setNumber("Mesh.Binary", 1)
            gmsh.write(str(self.mesh_path))
        sensor = CircleSensor(
            tissue, coords, mesh_coords, Group(2, [surf_entity], surf_group), radius
        )
        self.tissues[tissue].surf["entities"] = [new_entity]
        self.sensors[name] = sensor
        self.save()
        logger.info(f"Sensor '{name}' added.")

    def add_circle_sensors_on(self, coords, tissue, radius):
        """Add multiple circle sensors to the mesh.

        Parameters
        ----------
        coords : Mapping [str, Iterable [float]]
            The coordinates of the sensor.
        tissue : str
            The name of the tissue the sensor is on.
        radius : float
            The radius of the sensor [m].
        """
        for n, c in coords.items():
            self.add_circle_sensor_on(n, c, tissue, radius)

    def add_circle_sensors_from_tsv_on(self, tsv_path, tissue, radius):
        """Add multiple circle sensors to the mesh from a TSV file.

        Parameters
        ----------
        tsv_path : str, byte or os.PathLike
            The path to the TSV file.
        tissue : str
            The name of the tissue the sensor is on.
        radius : float
            The radius of the sensor [m].
        """
        tsv_path = Path(tsv_path)
        data = np.genfromtxt(
            tsv_path, delimiter="\t", skip_header=1, dtype=None, encoding="utf-8"
        )
        coords = {d[0]: [d[1], d[2], d[3]] for d in data}
        logger.info(f"{len(coords)} sensors coordinates extracted from '{tsv_path}'.")
        logger.debug(pformat(coords))
        return self.add_circle_sensors_on(coords, tissue, radius)

    def _get_tissue_nodes(self, tissue, dim):
        """Return all the nodes of the tissue in specified dimensio entities."""
        if dim == 2:
            entities = self.tissues[tissue].surf.entities
        elif dim == 3:
            entities = self.tissues[tissue].vol.entities
        logger.debug(
            (
                f"Acquiring nodes from tissue '{tissue}' "
                f"{'surface' if dim == 2 else 'volume'} with entities:\n{entities}"
            )
        )
        logger.debug(
            f"All {'surface' if dim == 2 else 'volume'} entities:"
            f"\n{gmsh.model.getEntities(dim)}"
        )
        nodes = [gmsh.model.mesh.getNodes(dim, e, True)[:2] for e in entities]
        logger.debug(f"Acquired {nodes[0][0].size} nodes:\n{nodes}")
        tags = np.hstack([t for t, _ in nodes])
        coords = np.hstack([c for _, c in nodes]).reshape((-1, 3))
        return tags, coords

    _get_tissue_surf_nodes = partialmethod(_get_tissue_nodes, dim=2)
    _get_tissue_vol_nodes = partialmethod(_get_tissue_nodes, dim=3)

    def _add_point_sensor(self, name, coords, nodes_tags, nodes_coords, tissue):
        """Add a point sensor."""
        dist = cdist([coords], nodes_coords).ravel()
        min_dist_idx = np.argmin(dist)
        node_tag = nodes_tags[min_dist_idx]
        mesh_coords = nodes_coords[min_dist_idx, :].ravel()
        entity, group = self._add_point_sensor_on_node(name, node_tag, mesh_coords)
        sensor = PointSensor(
            tissue, coords, mesh_coords, Group(0, [entity], group), node_tag
        )
        self["sensors"][name] = sensor

    def _add_point_sensor_on_node(self, name, node_tag, node_coords):
        """Add a point sensor on a node."""
        entity = gmsh.model.addDiscreteEntity(0)
        gmsh.model.mesh.addNodes(0, entity, [node_tag], node_coords)
        gmsh.model.mesh.addElementsByType(entity, 15, [], [node_tag])
        max_group = max([tag for dim, tag in gmsh.model.getPhysicalGroups(-1)])
        group = gmsh.model.addPhysicalGroup(0, [entity], max_group + 1)
        gmsh.model.setPhysicalName(0, group, name)
        return entity, group

    # Fields ---------------------------------------------------------------------------

    def field_from_elems(
        self, name, tissue, elems_tags, elems_vals, fill_val=None, formula="1"
    ):
        """Add a field to the mesh from element data.

        Parameters
        ----------
        name : str
            The name of the field. In the mesh, it will be added as '{tissue}_{name}'.
        tissue : str
            The tissue in which the field must be added.
        elems_tags : np.ndarray or Iterable [int]
            The tags of the elements in which the value is available.
        elems_vals : np.ndarray or Iterable
            The values of the field on the corresponding elements.
        fill_val : np.ndarray or Iterable
            The value to add in elements of the tissue that are not in `elems_tags`.
        formula : str
            The formula linking the field to a physical property.

        Raises
        ------
        KeyError
            If argument `tissue` does not correspond to a tissue of the mesh.
            If argument `name` refers to an already existing field.
        TypeError
            If argument `elems_tags` is neither a `numpy.ndarray` or a `Iterable` of
            `int`.
            If argument `elems_vals` is neither a `numpy.ndarray` or a `Iterable`.
            If argument `fill_val` is neither a `numpy.ndarray` or a `Iterable`.
        ValueError
            If argument `elems_vals` does not contain a scalar, vector or tensor field.
            If argument `fill_val` does not correspond to the values in `elems_vals`.
        """
        if tissue not in self.tissues:
            raise KeyError(f"Tissue '{tissue}' not found in model.")
        if name in self.tissues[tissue].fields:
            raise KeyError(f"Field '{name}' already exists in tissue '{tissue}'.")
        if not isinstance(elems_tags, (np.ndarray, Iterable)):
            raise TypeError(
                "Argument 'elems_tags' expects numpy.ndarray or Iterable of int."
            )
        elems_tags = np.array(elems_tags)
        if not isinstance(elems_vals, (np.ndarray, Iterable)):
            raise TypeError(
                "Argument 'elems_vals' expects numpy.ndarray or Iterable of int."
            )
        elems_vals = np.array(elems_vals).ravel()
        n_vals = int(elems_vals.size / elems_tags.size)
        field_types = {1: Field.SCALAR, 3: Field.VECTOR, 9: Field.TENSOR}
        if n_vals not in field_types:
            raise ValueError(
                "Argument 'elems_vals' must contain scalar, vector or tensor values."
            )
        field_type = field_types[n_vals]
        if not isinstance(fill_val, (np.ndarray, Iterable)):
            raise TypeError("Argument 'fill_val' expects numpy.ndarray or Iterable.")
        fill_val = np.array(fill_val).ravel()
        if fill_val.size != n_vals:
            raise ValueError(
                "Argument 'fill_val' must be of the same type and size as 'elems_vals'."
            )
        # TODO: Check formula

        with gmsh_open(self.mesh_path, logger) as gmsh:
            elems_tags, elems_vals = self._fill_empty_field_elems(
                tissue, elems_tags, elems_vals, n_vals, fill_val
            )
            view = self._add_field_view(name, tissue, elems_tags, elems_vals, n_vals)
            gmsh.option.setNumber("PostProcessing.SaveMesh", 0)
            gmsh.option.setNumber("Mesh.Binary", 1)
            gmsh.view.write(view, str(self.mesh_path), True)
        self.tissues[tissue].fields[name] = Field(field_type, view, formula)
        self.save()
        logger.info(f"Field '{name}' added in tissue '{tissue}'.")

    def field_from_array(
        self,
        name,
        field,
        affine,
        tissue,
        fill_val,
        formula="1",
        nearest=True,
        resize=True,
    ):
        """Add a field to the mesh from an array.

        Parameters
        ----------
        name : str
            The name of the field. In the mesh, it will be added as '{tissue}_{name}'.
        field : numpy.ndarray
            The field values.
        affine : numpy.ndarray
            The affine matrix of the field.
        tissue : str
            The tissue in which the field must be added.
        fill_val : np.ndarray or Iterable
            The value to add in elements of the tissue that are not in `elems_tags`.
        formula : str, optional
            The formula linking the field to a physical property. The default value is
            `'1'`.
        nearest : bool, optional
            If set to ``True``, no interpolation is performed. Otherwise, a linear
            interpolation is used. The default value is ``True``.
        resize : bool, optional
            If set to ``True``, the affine matrix is converted from [mm] to [m]. The
            default is ``True``.

        Raises
        ------
        TypeError
            If argument `field` is not a `numpy.ndarray`.
            If argument `affine` is not a `numpy.ndarray`.
        ValueError
            If argument `field` is not a 3D or 4D array containing a scalar, vector or
            tensor field.
            If argument `affine` is neither a (3, 4) nor a (4, 4) array.
        KeyError
            If argument `tissue` does not correspond to a tissue of the mesh.

        See Also
        --------
        FEM.field_from_array
        """
        if not isinstance(field, np.ndarray):
            raise TypeError("Argument 'field' expects type numpy.ndarray.")
        if field.ndim not in (3, 4):
            raise ValueError(
                (
                    "Argument 'field' must be a 3D or 4D array containing scalar, "
                    "vector or tensor values."
                )
            )
        if field.ndim == 4 and field.shape[-1] not in (1, 3, 9):
            raise ValueError(
                (
                    "Argument 'field' must be a 3D or 4D array containing scalar, "
                    "vector or tensor values."
                )
            )
        if not isinstance(affine, np.ndarray):
            raise TypeError("Argument 'affine' expects type numpy.ndarray.")
        if affine.shape not in ((3, 4), (4, 4)):
            raise ValueError("Argument 'affine' expects shape (3,4) or (4,4).")
        affine = np.vstack((affine[:3, :], np.array([0, 0, 0, 1])))
        # Convert [mm] to [m]
        if resize:
            affine = np.diag([1e-3] * 3 + [1]) @ affine
        if tissue not in self.tissues:
            raise KeyError(f"Tissue '{tissue}' not found in model.")

        coords = self._get_field_coords(field.shape, affine)
        elems_tags, elems_vals = self._interp_field(
            tissue, coords, field, "nearest" if nearest else "linear", fill_val
        )
        return self.field_from_elems(
            name, tissue, elems_tags, elems_vals, fill_val, formula
        )

    def field_from_nii(
        self, name, nii_path, tissue, fill_val, formula="1", nearest=True, resize=True
    ):
        """Add a field to the mesh from a NIFTI image.

        Parameters
        ----------
        name : str
            The name of the field. In the mesh, it will be added as '{tissue}_{name}'.
        nii_path : str, byte or os.PathLike
            The path to the NIFTI file containing the field.
        tissue : str
            The tissue in which the field must be added.
        fill_val : np.ndarray or Iterable
            The value to add in elements of the tissue that are not in `elems_tags`.
        formula : str, optional
            The formula linking the field to a physical property. The default value is
            `'1'`.
        nearest : bool, optional
            If set to ``True``, no interpolation is performed. Otherwise, a linear
            interpolation is used. The default value is ``True``.
        resize : bool, optional
            If set to ``True``, the affine matrix is converted from [mm] to [m]. The
            default is ``True``.

        Raises
        ------
        TypeError
            If argument `nii_path` is not a `str`, `byte` or `os.PathLike`.

        See Also
        --------
        FEM.field_from_array
        """
        nii_path = Path(nii_path)

        img = nib.load(str(nii_path))
        return self.field_from_array(
            name,
            img.get_fdata(),
            img.affine,
            tissue,
            fill_val,
            formula,
            nearest,
            resize,
        )

    def _get_tissue_elems(self, tissue, dim):
        """Return all the elements of the tissue in specified dimension."""
        if dim == 2:
            entities = self.tissues[tissue].surf.entities
        elif dim == 3:
            entities = self.tissues[tissue].vol.entities
        return np.hstack([gmsh.model.mesh.getElements(dim, e)[1] for e in entities])

    _get_tissue_surf_elems = partialmethod(_get_tissue_elems, dim=2)
    _get_tissue_vol_elems = partialmethod(_get_tissue_elems, dim=3)

    def _get_tissue_elems_coords(self, tissue, dim):
        """Return the barycenters of all the elements of the tissue in specified
        dimension.
        """
        if dim == 2:
            entities = self.tissues[tissue].surf.entities
            elems_type = 2  # Triangle
        elif dim == 3:
            entities = self.tissues[tissue].vol.entities
            elems_type = 4  # Tetrahedron
        return np.hstack(
            [
                gmsh.model.mesh.getBarycenters(elems_type, e, fast=False, primary=False)
                for e in entities
            ]
        ).reshape((-1, 3))

    _get_tissue_surf_elems_coords = partialmethod(_get_tissue_elems_coords, dim=2)
    _get_tissue_vol_elems_coords = partialmethod(_get_tissue_elems_coords, dim=3)

    def _fill_empty_field_elems(self, tissue, elems_tags, elems_vals, n_vals, fill_val):
        """Add a default value to empty elements."""
        all_elems_tags = self._get_tissue_vol_elems(tissue)
        empty_elems_idx = np.isin(
            all_elems_tags, elems_tags, assume_unique=True, invert=True
        )
        if np.any(empty_elems_idx):
            logger.debug(f"Filling {np.nonzero(empty_elems_idx).size} elements.")
            empty_elems_tags = all_elems_tags[empty_elems_idx]
            empty_elems_vals = np.broadcast_to(
                np.array(fill_val), (1, int(empty_elems_tags.size * n_vals))
            ).ravel()
            elems_tags = np.hstack((elems_tags.ravel(), empty_elems_tags))
            elems_vals = np.hstack((elems_vals.ravel(), empty_elems_vals))
        return elems_tags, elems_vals

    def _add_field_view(self, name, tissue, elems_tags, elems_vals, n_vals):
        """Add a view with the field values."""
        model = gmsh.model.list()[0]
        view = gmsh.view.add(f"{tissue}_{name}")
        elems_vals = elems_vals.reshape((-1, n_vals))
        logger.debug(f"{elems_tags.shape}, {elems_vals.shape}, {n_vals}")
        gmsh.view.addModelData(
            view, 0, model, "ElementData", elems_tags.ravel(), elems_vals
        )
        return view

    def _get_field_coords(self, shape, affine):
        """Convert cell indices into real coordinates."""
        flat_idx = np.arange(np.prod(shape[:3]))
        idx = np.vstack(np.unravel_index(flat_idx, shape[:3])).T
        coords = nib.affines.apply_affine(affine, idx)
        return coords

    def _interp_field(self, tissue, coords, field, method, fill_val):
        """Interpolate a field on a mesh grid."""
        x = np.unique(coords[:, 0])
        y = np.unique(coords[:, 1])
        z = np.unique(coords[:, 2])
        interpolate = RegularGridInterpolator(
            (x, y, z), field, method=method, bounds_error=False, fill_value=fill_val
        )
        with gmsh_open(self.mesh_path, logger) as gmsh:
            elems_tags = self._get_tissue_vol_elems(tissue)
            elems_coords = self._get_tissue_vol_elems_coords(tissue)
        elems_vals = interpolate(elems_coords)
        return elems_tags, elems_vals
