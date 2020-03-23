from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

import numpy as np
import nibabel as nib
import gmsh

from shamo import FEModel

MODEL_PATH = str(Path("tests/data/model_1"))


def _check_model_anisotropy(model, name, anisotropy_type, formula):
    assert(name in model.anisotropy)
    assert(model.anisotropy[name].anisotropy_type == anisotropy_type)
    assert(model.anisotropy[name].formula == formula)


def test_add_anisotropy_from_array_scalar():
    with TemporaryDirectory() as parent_path:
        # Load model
        shutil.copytree(MODEL_PATH, str(Path(parent_path) / "model_1"))
        model_path = str(Path(parent_path) / "model_1/model_1.json")
        model = FEModel.load(model_path)
        # Generate anisotropy
        field = np.zeros((2, 2, 2))
        field[1, 1, 1] = 1
        affine = np.diag((10, 10, 10, 1))
        # Add anisotropy
        model.add_anisotropy_from_array(field, affine, "b", 0, formula="3*<b>",
                                        suffix="test")
        model.save()
        # Test the model
        _check_model_anisotropy(model, "b_test", "scalar", "3*<b>")


def test_add_anisotropy_from_array_tensor():
    with TemporaryDirectory() as parent_path:
        # Load model
        shutil.copytree(MODEL_PATH, str(Path(parent_path) / "model_1"))
        model_path = str(Path(parent_path) / "model_1/model_1.json")
        model = FEModel.load(model_path)
        # Generate anisotropy
        field = np.zeros((2, 2, 2, 9))
        field[1, 1, 1, :] = (1, 0, 0, 0, 1, 0, 0, 0, 1)
        affine = np.diag((10, 10, 10, 1))
        # Add anisotropy
        model.add_anisotropy_from_array(field, affine, "b",
                                        (1, 0, 0, 0, 1, 0, 0, 0, 1),
                                        formula="3*<b>", suffix="test")
        model.save()
        # Test the model
        _check_model_anisotropy(model, "b_test", "tensor", "3*<b>")


def test_add_anisotropy_from_nii_scalar():
    with TemporaryDirectory() as parent_path:
        # Load model
        shutil.copytree(MODEL_PATH, str(Path(parent_path) / "model_1"))
        model_path = str(Path(parent_path) / "model_1/model_1.json")
        model = FEModel.load(model_path)
        # Generate anisotropy
        field = np.zeros((2, 2, 2))
        field[1, 1, 1] = 1
        affine = np.diag((10, 10, 10, 1))
        image_path = str(Path(parent_path) / "field.nii")
        img = nib.Nifti1Image(field, affine)
        img.to_filename(image_path)
        # Add anisotropy
        model.add_anisotropy_from_nii(image_path, "b", 0, formula="3*<b>",
                                      suffix="test")
        model.save()
        # Test the model
        _check_model_anisotropy(model, "b_test", "scalar", "3*<b>")


def test_add_anisotropy_from_nii_tensor():
    with TemporaryDirectory() as parent_path:
        # Load model
        shutil.copytree(MODEL_PATH, str(Path(parent_path) / "model_1"))
        model_path = str(Path(parent_path) / "model_1/model_1.json")
        model = FEModel.load(model_path)
        # Generate anisotropy
        field = np.zeros((2, 2, 2, 9))
        field[1, 1, 1, :] = (1, 0, 0, 0, 1, 0, 0, 0, 1)
        affine = np.diag((10, 10, 10, 1))
        image_path = str(Path(parent_path) / "field.nii")
        img = nib.Nifti1Image(field, affine)
        img.to_filename(image_path)
        # Add anisotropy
        model.add_anisotropy_from_nii(image_path, "b", 0, formula="3*<b>",
                                      suffix="test")
        model.save()
        # Test the model
        _check_model_anisotropy(model, "b_test", "tensor", "3*<b>")
