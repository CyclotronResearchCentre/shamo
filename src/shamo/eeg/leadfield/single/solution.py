"""Implement `SolEEGLeadfield` class."""
import h5py
import numpy as np

from shamo.core.problems.single import CompSensors
from shamo.core.solutions.single import SolGetDP


class SolEEGLeadfield(SolGetDP):
    """Store information about an EEG leadfield matrix.

    Parameters
    ----------
    name : str
        The name of the solution.
    parent_path : str, byte or os.PathLike
        The path to the parent directory of the solution.

    Other Parameters
    ----------------
    sigmas : dict [str, list [float, str]]
        The electrical conductivity of the tissues.
    model_json_path : str
        The relative path of the model JSON file.
    markers : list [str]
        The names of the markers.
    reference : list [str]
        The name of the reference.
    rois : list [str]
        The names of the tissues of the region of interest.
    sensors : list [str]
        The names of the active sensors.
    shape : tuple [int]
        The shape of the matrix.
    use_grid : bool
        If ``True``, the source space is based on a grid.
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        self.update(
            {
                "markers": kwargs.get("markers", []),
                "reference": kwargs.get("reference", []),
                "rois": kwargs.get("rois", []),
                "sensors": kwargs.get("sensors", []),
                "shape": tuple(kwargs.get("shape", [])),
                "use_grid": kwargs.get("use_grid", False),
            }
        )

    @property
    def matrix_path(self):
        """Return the path to the matrix HDF5 file.

        Returns
        -------
        pathlib.Path
            The path to the matrix HDF5 file.
        """
        return self.path / f"{self.name}.hdf5"

    @property
    def shape(self):
        """Return the shape of the matrix.

        Returns
        -------
        tuple [int]
            The shape of the matrix.
        """
        return self["shape"]

    @property
    def n_sensors(self):
        """Return the number of active sensors.

        Returns
        -------
        int
            The number of active sensors.
        """
        return self["shape"][0]

    @property
    def n_sources(self):
        """Return the number of sources.

        Returns
        -------
        int
            The number of sources.
        """
        return self["shape"][1]

    @property
    def markers(self):
        """Return the names of the markers.

        Returns
        -------
        list [str]
            The names of the markers.
        """
        return self["markers"]

    @property
    def reference(self):
        """Return the name of the reference.

        Returns
        -------
        str
            The name of the reference.
        """
        return self["reference"][0]

    @property
    def sensors(self):
        """Return the names of the active sensors.

        Returns
        -------
        list [str]
            The names of the active sensors.
        """
        return self["sensors"]

    @property
    def rois(self):
        """Return the names of the tissues of the region of interest.

        Returns
        -------
        list [str]
            The names of the tissues of the region of interest.
        """
        return self["rois"]

    @property
    def use_grid(self):
        """Return ``True`` if the source space is based on a grid.

        Returns
        -------
        bool
            ``True`` if the source space is based on a grid, ``False`` otherwise.
        """
        return self["use_grid"]

    @property
    def source_sp_path(self):
        """Return the path to the source space file.

        Returns
        -------
        pathlib.Path
            The path to the source space file.
        """
        if self.use_grid:
            return self.path / f"{self.name}_mask.nii"
        return self.path / f"{self.name}_elems.npz"

    def set_matrix(self, matrix):
        """Set the matrix of the solution.

        Parameters
        ----------
        numpy.ndarray
            The leadfield matrix.
        """
        with h5py.File(self.matrix_path, "w") as f:
            data = f.create_dataset(
                "e_field", matrix.shape, dtype="f", compression="lzf"
            )
            data[...] = matrix
        self["shape"] = matrix.shape

    def get_matrix(self):
        """Return the matrix.

        Returns
        -------
        h5py.Dataset
            The dataset containing the matrix.
        """
        return h5py.File(self.matrix_path, "r")["e_field"]
