"""Implement the `FEModel` class.

This module implements the `FEModel` class which holds the data corresponding
to a finite elements model specific to a subject.
"""
from pathlib import Path

from shamo.core import DirObject
from .tissue import Tissue
from .sensor import Sensor
from .anisotropy import Anisotropy
from .sources.fe_source import FESource


class FEModel(DirObject):
    """A subject specifi model.

    Parameters
    ----------
    name : str
        The name given to the model.
    parent_path : str
        The path to the parent directory of the model.

    Other Parameters
    ----------------
    mesh_path : str
        The path to the ``.msh`` file of the model.
    tissues : dict [str, dict]
        The tissues of the model.
    sensors : dict [str, dict]
        The sensors of the model.
    anisotropy : dict [str, dict]
        The anisotropy of the model.

    See Also
    --------
    shamo.core.objects.DirObject
        To load and save this object, see its parent class.
    """

    from ._geometry import (
        mesh_from_labels,
        mesh_from_nii,
        mesh_from_masks,
        mesh_from_niis,
        get_tissues_from_mesh,
    )
    from ._sensors import add_sensor, add_sensors
    from ._anisotropy import (
        add_anisotropy_from_elements,
        add_anisotropy_from_array,
        add_anisotropy_from_nii,
    )
    from ._source import add_sources, source_exists, get_source

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path)
        # Mesh path
        self["mesh_path"] = kwargs.get("mesh_path", None)
        # Nodes count
        self["n_nodes"] = int(kwargs.get("n_nodes", 0))
        # Tissues
        tissues = kwargs.get("tissues", {})
        self["tissues"] = {name: Tissue(**data) for name, data in tissues.items()}
        # Sensors
        sensors = kwargs.get("sensors", {})
        self["sensors"] = {name: Sensor(**data) for name, data in sensors.items()}
        # Anisotropy
        anisotropy = kwargs.get("anisotropy", {})
        self["anisotropy"] = {
            name: Anisotropy(**data) for name, data in anisotropy.items()
        }
        # Sources
        sources = kwargs.get("sources", [])
        self["sources"] = [FESource(**data) for data in sources]

    @property
    def mesh_path(self):
        """Return the path to the ``.msh`` file of the model.

        Returns
        -------
        str
            The path to the ``.msh`` file of the model.

        Raises
        ------
        FileNotFoundError
            If the model does not contain a ``.msh`` file.
            If the ``.msh`` file does not exist.
        """
        # Check if the mesh file exists
        if self["mesh_path"] is None:
            raise FileNotFoundError("The model does not contain a mesh file.")
        path = Path(self.path) / self["mesh_path"]
        if not path.exists():
            raise FileNotFoundError(("The specified mesh file no longer " "exists."))
        return str(path)

    @property
    def n_nodes(self):
        """Return the total number of nodes in the model.

        Returns
        -------
        int
            The total number of nodes in the model.
        """
        return self["n_nodes"]

    @property
    def tissues(self):
        """Return the tissues of the model.

        Returns
        -------
        dict [str, shamo.model.tissue.Tissue]
            The tissues of the model.
        """
        return self["tissues"]

    @property
    def sensors(self):
        """Return the sensors of the model.

        Returns
        -------
        dict [str, shamo.model.sensor.Sensor]
            The sensors of the model.
        """
        return self["sensors"]

    @property
    def anisotropy(self):
        """Return the anisotropy of the model.

        Returns
        -------
        dict [str, shamo.model.anisotropy.Anisotropy]
            The anisotropy of the model.
        """
        return self["anisotropy"]

    @property
    def sources(self):
        """Return the sources of the model.

        Returns
        -------
        list [shamo.model.sources.fe_source.FESource]
            The sources of the model.
        """
        return self["sources"]
