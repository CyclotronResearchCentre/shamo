"""Implement the `ComGridSampler` class."""
import logging

import nibabel as nib
import numpy as np
import re

from .abc import CompABC
from shamo.utils.onelab import read_vector_file, pos_to_nii

logger = logging.getLogger(__name__)


class CompGridSampler(CompABC):
    """Store information about a space grid sampler.

    A grid sampler is used to convert outputs from GetDP into a NII file more suitable
    for neuroimaging studies.

    Other Parameters
    ----------------
    affine : numpy.ndarray
        The affine matrix of the grid.
    shape : tuple [int]
            The shape of the grid.
    mask : numpy.ndarray
            The mask of the grid.
    """

    def __init__(self, **kwargs):
        super().__init__(
            affine=kwargs.get("affine", []),
            shape=kwargs.get("shape", []),
            mask=kwargs.get("mask", None),
        )

    @property
    def use_grid(self):
        """Return wether or not the grid can be used.

        Returns
        -------
        bool
            Return ``True`` if the grid can be used, ``False`` otherwise.
        """
        return True if self["affine"] != [] and self["shape"] != [] else False

    @property
    def affine(self):
        """Return the affine matrix of the grid.

        Returns
        -------
        numpy.ndarray
            The affine matrix of the grid.
        """
        return self["affine"]

    @property
    def shape(self):
        """Return the shape of the grid.

        Returns
        -------
        tuple [int]
            The shape of the grid.
        """
        return self["shape"]

    @property
    def mask(self):
        """Return the mask of the grid.

        Returns
        -------
        numpy.ndarray
            The mask of the grid.
        """
        return self["mask"]

    def set(self, affine, shape, mask=None, resize=False):
        """Set the grid component.

        Parameters
        ----------
        affine : numpy.ndarray
            The affine matrix of the grid.
        shame : tuple [int]
            The shape of the grid.
        mask : numpy.ndarray, optional
            The mask of the grid. If set to ``None``, no mask is applied to the
            resulting data. (The default is ``None``)
        resize : bool, optional
            If set to ``True``, the affine matrix is rescaled from meters to
            millimeters. (the default is ``False``)
        """
        self["affine"] = np.vstack((affine[:3, :], np.array([0, 0, 0, 1])))
        if resize:
            self["affine"] = np.diag([1e-3] * 3 + [1]) @ self["affine"]
        self["shape"] = shape
        self["mask"] = mask

    def check(self, name, **kwargs):
        """Check is the grid is properly set.

        Parameters
        ----------
        name : str
            The name of the grid.

        Raises
        ------
        TypeError
            If argument `affine` is not a `numpy.ndarray`.
        ValueError
            If argument `affine` is not (3, 4) or (4, 4) `numpy.ndarray`.
            If argument `shape` is not a 3D shape.
        """
        if self.use_grid:
            logger.info(f"Checking grid sampler '{name}'.")
            if not isinstance(self["affine"], np.ndarray):
                raise TypeError("Argument 'affine' expects type numpy.ndarray.")
            if self["affine"].shape not in ((3, 4), (4, 4)):
                raise ValueError("Argument 'affine' expects shape (3,4) or (4,4).")
            if len(self["shape"]) != 3:
                raise ValueError("Argument 'shape' expects 3 values.")

    def to_pro_param(self, **kwargs):
        """Return if the grid can be used.

        Returns
        -------
        bool
            Return ``True`` if the grid is set.
        """
        return self.use_grid

    def to_py_param(self, **kwargs):
        """Return the parameters required to render python template.

        Returns
        -------
        dict [str, str]
            The parameters required to render python template.
        """
        if self.use_grid:
            return {
                "affine": str(self.affine.tolist()),
                "shape": str(self.shape),
                "mask": str(self.mask.astype(int).tolist())
                if self.mask is not None
                else None,
            }
        else:
            return None

    def nii_from_pos(self, src, dst):
        """Convert a POS file into a NII file.

        Parameters
        ----------
        src : str, byte or os.PathLike
            The path to the POS file to convert.
        dst : str, byte or os.PathLike
            The path where the generated NII image must be saved.
        Returns
        -------
        nibabel.Nifti1Image
            The generated NII image.
        """
        return pos_to_nii(src, dst, self.affine, self.shape, mask=self.mask)
