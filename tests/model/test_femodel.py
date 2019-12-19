from pathlib import Path
from tempfile import TemporaryDirectory

import nibabel as nib
import numpy as np

from shamo.model import FEModel, MeshConfig


def test_fem_from_labels():
    with TemporaryDirectory() as parent_path:
        model = FEModel("test", parent_path)
        labels = np.zeros((11, 11, 11))
        labels[2:-2, 2:-2, 2:-2] = 1
        labels[4:-4, 4:-4, 4:-4] = 2
        affine = np.identity(4)
        scale = (1, 1, 1)
        tissues = ["tissue_1", "tissue_2"]
        mesh_config = MeshConfig(facet_distance=0.1, cell_size=0.75,
                                 cell_radius_edge_ratio=1.5)
        model.fem_from_labels(labels, tissues, affine, scale, mesh_config)
        assert(model.mesh_path
               == str(Path(model.path) / "{}.msh".format(model.name)))
        assert(Path(model.mesh_path).exists())
        assert(Path(model.mesh_path).is_file())
        assert("tissue_1" in model.tissues)
        assert("tissue_2" in model.tissues)


def test_fem_from_nii():
    with TemporaryDirectory() as parent_path:
        model = FEModel("test", parent_path)
        labels = np.zeros((11, 11, 11))
        labels[2:-2, 2:-2, 2:-2] = 1
        labels[4:-4, 4:-4, 4:-4] = 2
        affine = np.identity(4)
        tissues = ["tissue_1", "tissue_2"]
        mesh_config = MeshConfig(facet_distance=0.1, cell_size=0.75,
                                 cell_radius_edge_ratio=1.5)
        image_path = str(Path(parent_path) / "labels.nii")
        image = nib.Nifti1Image(labels, affine)
        image.to_filename(image_path)
        model.fem_from_nii(image_path, tissues, mesh_config)
        assert(model.mesh_path
               == str(Path(model.path) / "{}.msh".format(model.name)))
        assert(Path(model.mesh_path).exists())
        assert(Path(model.mesh_path).is_file())
        assert("tissue_1" in model.tissues)
        assert("tissue_2" in model.tissues)


def test_fem_from_masks():
    with TemporaryDirectory() as parent_path:
        model = FEModel("test", parent_path)
        mask1 = np.zeros((11, 11, 11), dtype=np.bool)
        mask1[2:-2, 2:-2, 2:-2] = True
        mask2 = np.zeros((11, 11, 11), dtype=np.bool)
        mask2[4:-4, 4:-4, 4:-4] = True
        tissue_masks = {"tissue_1": mask1, "tissue_2": mask2}
        affine = np.identity(4)
        scale = (1, 1, 1)
        mesh_config = MeshConfig(facet_distance=0.1, cell_size=0.75,
                                 cell_radius_edge_ratio=1.5)
        model.fem_from_masks(tissue_masks, affine, scale, mesh_config)
        assert(model.mesh_path
               == str(Path(model.path) / "{}.msh".format(model.name)))
        assert(Path(model.mesh_path).exists())
        assert(Path(model.mesh_path).is_file())
        assert("tissue_1" in model.tissues)
        assert("tissue_2" in model.tissues)


def test_fem_from_niis():
    with TemporaryDirectory() as parent_path:
        model = FEModel("test", parent_path)
        affine = np.identity(4)
        mask1 = np.zeros((11, 11, 11), dtype=np.uint8)
        mask1[2:-2, 2:-2, 2:-2] = True
        image1_path = str(Path(parent_path) / "mask1.nii")
        image1 = nib.Nifti1Image(mask1, affine)
        image1.to_filename(image1_path)
        mask2 = np.zeros((11, 11, 11), dtype=np.uint8)
        mask2[4:-4, 4:-4, 4:-4] = True
        image2_path = str(Path(parent_path) / "mask2.nii")
        image2 = nib.Nifti1Image(mask2, affine)
        image2.to_filename(image2_path)
        tissue_paths = {"tissue_1": image1_path, "tissue_2": image2_path}
        mesh_config = MeshConfig(facet_distance=0.1, cell_size=0.75,
                                 cell_radius_edge_ratio=1.5)
        model.fem_from_niis(tissue_paths, mesh_config)
        assert(model.mesh_path
               == str(Path(model.path) / "{}.msh".format(model.name)))
        assert(Path(model.mesh_path).exists())
        assert(Path(model.mesh_path).is_file())
        assert("tissue_1" in model.tissues)
        assert("tissue_2" in model.tissues)
