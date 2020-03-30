from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import nibabel as nib
import gmsh

from shamo import FEModel, MeshConfig


def _check_model_mesh(model, tissues):
    # Check structure
    assert(Path(model.path).exists())
    assert(Path(model.json_path).exists())
    assert(Path(model.mesh_path).exists())
    # Check model attributes
    gmsh.initialize()
    gmsh.open(model.mesh_path)
    vol_groups = gmsh.model.getPhysicalGroups(3)
    vols = {gmsh.model.getPhysicalName(*group): group[1]
            for group in vol_groups}
    surf_groups = gmsh.model.getPhysicalGroups(2)
    surfs = {gmsh.model.getPhysicalName(*group): group[1]
             for group in surf_groups}
    for name in tissues:
        assert(name in model.tissues)
        assert(name in vols)
        assert(vols[name] == model.tissues[name].volume_group)
        assert(name in surfs)
        assert(surfs[name] == model.tissues[name].surface_group)
    gmsh.finalize()


def test_mesh_from_labels():
    with TemporaryDirectory() as parent_path:
        model = FEModel("test", parent_path)
        labels = np.ones((11, 11, 11), dtype=np.uint8)
        labels[3:-3, 3:-3, 3:-3] = 2
        labels[2:-5, 2:-5, 2:-5] = 3
        tissues = ["a", "b", "c"]
        affine = np.diag([1, 1, 1, 1])
        mesh_config = MeshConfig(facet_distance=1.5, cell_size=1)
        model.mesh_from_labels(labels, tissues, affine, mesh_config)
        model.save()
        # Test the model
        _check_model_mesh(model, tissues)


def test_mesh_from_nii():
    with TemporaryDirectory() as parent_path:
        model = FEModel("test", parent_path)
        labels = np.ones((11, 11, 11), dtype=np.uint8)
        labels[3:-3, 3:-3, 3:-3] = 2
        labels[2:-5, 2:-5, 2:-5] = 3
        tissues = ["a", "b", "c"]
        affine = np.diag([1, 1, 1, 1])
        image_path = str(Path(parent_path) / "labels.nii")
        img = nib.Nifti1Image(labels, affine)
        img.to_filename(image_path)
        mesh_config = MeshConfig(facet_distance=1.5, cell_size=1)
        model.mesh_from_nii(image_path, tissues, mesh_config)
        model.save()
        # Test the model
        _check_model_mesh(model, tissues)


def test_mesh_from_masks():
    with TemporaryDirectory() as parent_path:
        model = FEModel("test", parent_path)
        mask1 = np.ones((11, 11, 11), dtype=np.uint8)
        mask1[3:-3, 3:-3, 3:-3] = 0
        mask1[2:-5, 2:-5, 2:-5] = 0
        mask2 = np.zeros((11, 11, 11), dtype=np.uint8)
        mask2[3:-3, 3:-3, 3:-3] = 1
        mask2[2:-5, 2:-5, 2:-5] = 0
        mask3 = np.zeros((11, 11, 11), dtype=np.uint8)
        mask3[2:-5, 2:-5, 2:-5] = 1
        tissue_masks = {"a": mask1, "b": mask2, "c": mask3}
        affine = np.diag([1, 1, 1, 1])
        mesh_config = MeshConfig(facet_distance=1.5, cell_size=1)
        model.mesh_from_masks(tissue_masks, affine, mesh_config)
        model.save()
        # Test the model
        _check_model_mesh(model, list(tissue_masks.keys()))


def test_mesh_from_niis():
    with TemporaryDirectory() as parent_path:
        model = FEModel("test", parent_path)
        affine = np.diag([1, 1, 1, 1])
        mask1_path = str(Path(parent_path) / "mask1.nii")
        mask1 = np.ones((11, 11, 11), dtype=np.uint8)
        mask1[3:-3, 3:-3, 3:-3] = 0
        mask1[2:-5, 2:-5, 2:-5] = 0
        img = nib.Nifti1Image(mask1, affine)
        img.to_filename(mask1_path)
        mask2_path = str(Path(parent_path) / "mask2.nii")
        mask2 = np.zeros((11, 11, 11), dtype=np.uint8)
        mask2[3:-3, 3:-3, 3:-3] = 1
        mask2[2:-5, 2:-5, 2:-5] = 0
        img = nib.Nifti1Image(mask2, affine)
        img.to_filename(mask2_path)
        mask3_path = str(Path(parent_path) / "mask3.nii")
        mask3 = np.zeros((11, 11, 11), dtype=np.uint8)
        mask3[2:-5, 2:-5, 2:-5] = 1
        img = nib.Nifti1Image(mask3, affine)
        img.to_filename(mask3_path)
        tissue_paths = {"a": mask1_path, "b": mask2_path, "c": mask3_path}
        mesh_config = MeshConfig(facet_distance=1.5, cell_size=1)
        model.mesh_from_niis(tissue_paths, mesh_config)
        model.save()
        # Test the model
        _check_model_mesh(model, list(tissue_paths.keys()))
