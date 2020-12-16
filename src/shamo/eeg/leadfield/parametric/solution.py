"""Implement `SolParamEEGLeadfield` class."""
from shamo.core.solutions.parametric import SolParamGetDP
from shamo.eeg import SolEEGLeadfield


class SolParamEEGLeadfield(SolParamGetDP):
    """Store information about an EEG leadfield matrix.

    Parameters
    ----------
    name : str
        The name of the solution.
    parent_path : str, byte or os.PathLike
        The path to the parent directory of the solution.

    Other Parameters
    ----------------
    sub_json_paths : list [str]
        The relative paths to the sub-solutions.
    sigmas : dict [str, list [shamo.DistABC, str]]
        The electrical conductivity of the tissues.
    model_json_path : str
        The relative path to the model JSON file.
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
    def sub_class(self):
        return SolEEGLeadfield

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
        return self["reference"]

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
        return self["use_grid"]

    def finalize(self, **kwargs):
        """Finalize the solution."""
        self._get_sub_json_paths()
        sub_sols = self.get_sub_sols()
        sub_sol = sub_sols[0]
        self.update({"shape": sub_sol.shape, "sensors": sub_sol.sensors})
        self.save()
