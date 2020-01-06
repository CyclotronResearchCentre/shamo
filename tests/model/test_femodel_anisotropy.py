from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

import nibabel as nib
import numpy as np
import gmsh

from shamo.model import FEModel, Anisotropy

# TODO: Fix the 3 following tests.
"""def test_add_anisotropy_from_elements_scalar():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        in_tissue = "b"
        gmsh.initialize()
        gmsh.open(model.mesh_path)
        _, element_tags, _ = gmsh.model.mesh.getElements(
            3, model.tissues[in_tissue].volume_entity[0])
        element_tags = np.array(element_tags)
        element_values = np.arange(element_tags.size)
        gmsh.finalize()
        model.add_anisotropy_from_elements(element_tags,
                                                     element_values,
                                                     in_tissue, 0, formula="1")
        assert("b" in model.anisotropy)
        assert(model.anisotropy["b"].anisotropy_type == Anisotropy.SCALAR)


def test_add_anisotropy_from_elements_vector():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        in_tissue = "b"
        gmsh.initialize()
        gmsh.open(model.mesh_path)
        _, element_tags, _ = gmsh.model.mesh.getElements(
            3, model.tissues[in_tissue].volume_entity[0])
        element_tags = np.array(element_tags)
        element_values = np.broadcast_to(np.arange(element_tags.size),
                                         (3, element_tags.size)).T.flatten()
        gmsh.finalize()
        model.add_anisotropy_from_elements(element_tags,
                                                     element_values,
                                                     in_tissue, (0, 0, 0),
                                                     formula="1")
        assert("b" in model.anisotropy)
        assert(model.anisotropy["b"].anisotropy_type == Anisotropy.VECTOR)


def test_add_anisotropy_from_elements_tensor():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        in_tissue = "b"
        gmsh.initialize()
        gmsh.open(model.mesh_path)
        _, element_tags, _ = gmsh.model.mesh.getElements(
            3, model.tissues[in_tissue].volume_entity[0])
        element_tags = np.array(element_tags)
        element_values = np.broadcast_to(np.arange(element_tags.size),
                                         (9, element_tags.size)).T.flatten()
        gmsh.finalize()
        model.add_anisotropy_from_elements(element_tags,
                                                     element_values,
                                                     in_tissue, (1, 0, 0,
                                                                 0, 1, 0,
                                                                 0, 0, 1),
                                                     formula="1")
        assert("b" in model.anisotropy)
        assert(model.anisotropy["b"].anisotropy_type == Anisotropy.TENSOR)
"""


def test_add_anisotropy_from_array_scalar():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        in_tissue = "b"
        field = np.zeros((2, 2, 2))
        field[1, :, :] = 1
        affine = np.diag([10, 10, 10, 1])
        model.add_anisotropy_from_array(field, affine, in_tissue,
                                        fill_value=0)
        assert("b" in model.anisotropy)
        assert(model.anisotropy["b"].anisotropy_type == Anisotropy.SCALAR)


def test_add_anisotropy_from_array_vector():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        in_tissue = "b"
        field = np.zeros((2, 2, 2, 3))
        field[1, :, :, 0] = 1
        affine = np.diag([10, 10, 10, 1])
        model.add_anisotropy_from_array(field, affine, in_tissue,
                                        fill_value=(0, 0, 0))
        assert("b" in model.anisotropy)
        assert(model.anisotropy["b"].anisotropy_type == Anisotropy.VECTOR)


def test_add_anisotropy_from_array_tensor():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        in_tissue = "b"
        field = np.zeros((2, 2, 2, 9))
        field[:, :, :, 0] = 1
        field[:, :, :, 4] = 1
        field[:, :, :, 8] = 1
        affine = np.diag([10, 10, 10, 1])
        model.add_anisotropy_from_array(field, affine, in_tissue,
                                        fill_value=(1, 0, 0,
                                                    0, 1, 0,
                                                    0, 0, 1))
        assert("b" in model.anisotropy)
        assert(model.anisotropy["b"].anisotropy_type == Anisotropy.TENSOR)


def test_add_anisotropy_from_nii_scalar():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        in_tissue = "b"
        field = np.zeros((2, 2, 2))
        field[1, :, :] = 1
        affine = np.diag([10, 10, 10, 1])
        image_path = str(Path(parent_path) / "field.nii")
        image = nib.Nifti1Image(field, affine)
        image.to_filename(image_path)
        model.add_anisotropy_from_nii(image_path, in_tissue,
                                      fill_value=0)
        assert("b" in model.anisotropy)
        assert(model.anisotropy["b"].anisotropy_type == Anisotropy.SCALAR)


def test_add_anisotropy_from_nii_vector():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        in_tissue = "b"
        field = np.zeros((2, 2, 2, 3))
        field[1, :, :, 0] = 1
        affine = np.diag([10, 10, 10, 1])
        image_path = str(Path(parent_path) / "field.nii")
        image = nib.Nifti1Image(field, affine)
        image.to_filename(image_path)
        model.add_anisotropy_from_nii(image_path, in_tissue,
                                      fill_value=(0, 0, 0))
        assert("b" in model.anisotropy)
        assert(model.anisotropy["b"].anisotropy_type == Anisotropy.VECTOR)


def test_add_anisotropy_from_nii_tensor():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        in_tissue = "b"
        field = np.zeros((2, 2, 2, 9))
        field[:, :, :, 0] = 1
        field[:, :, :, 4] = 1
        field[:, :, :, 8] = 1
        affine = np.diag([10, 10, 10, 1])
        image_path = str(Path(parent_path) / "field.nii")
        image = nib.Nifti1Image(field, affine)
        image.to_filename(image_path)
        model.add_anisotropy_from_nii(image_path, in_tissue,
                                      fill_value=(1, 0, 0,
                                                  0, 1, 0,
                                                  0, 0, 1))
        assert("b" in model.anisotropy)
        assert(model.anisotropy["b"].anisotropy_type == Anisotropy.TENSOR)
