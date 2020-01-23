"""Implement the `FEModel` class.

This module implements the `FEModel` class which holds the data corresponding
to a finite elements model.
"""
from pathlib import Path
import shutil

from shamo.core import JSONObject
from .tissue import Tissue
from .sensor import Sensor
from .anisotropy import Anisotropy


class FEModel(JSONObject):
    """Allow generation of a finite element model.

    Parameters
    ----------
    name : str
        The name given to the model.
    parent_path : str
        The path to the parent directory of the model.
    parents : bool, optional
        If set to `True`, any missing level in the tree is created. (The
        default is `True`).
    exist_ok : bool, optional
        If set to `True`, no exception is raised if the directory already
        exists. (The default is `True`).
    mesh_path : str, optional
        The path to the `.msh` file of the model. (The default is `None`).
    tissues : dict[str: dict], optional
        The tissues of the model. (The default is `None`).
    anisotropy : dict[str: dict], optional
        The anisotropy of the model. (the default is `None`).

    Attributes
    ----------
    name
    path
    json_path
    mesh_path
    tissues
    sensors
    anisotropy

    See Also
    --------
    JSONObject
    """

    from ._geometry import (fem_from_labels, fem_from_nii, fem_from_masks,
                            fem_from_niis, get_tissues_from_mesh)
    from ._sensors import (add_sensor_on_tissue, add_sensors_on_tissue)
    from ._anisotropy import (add_anisotropy_from_elements,
                              add_anisotropy_from_array,
                              add_anisotropy_from_nii)

    def __init__(self, name, parent_path, parents=True, exist_ok=True,
                 mesh_path=None, tissues=None, sensors=None, anisotropy=None):
        super().__init__(name, parent_path, parents, exist_ok)
        # Set `mesh_path`
        if mesh_path is not None:
            if (Path(self.path) / mesh_path).exists():
                self["mesh_path"] = mesh_path
            elif str(Path(mesh_path).parents[0]) != self.path:
                # Copy file inside `FEModel` directory and rename it
                new_mesh_path = Path(self.path) / "{}.msh".format(self.name)
                shutil.copy(mesh_path, new_mesh_path)
                self["mesh_path"] = str(new_mesh_path.relative_to(self.path))
            else:
                self["mesh_path"] = str(Path(mesh_path).relative_to(self.path))
        if tissues is not None:
            self["tissues"] = {name: Tissue(**tissue)
                               for name, tissue in tissues.items()}
        if sensors is not None:
            self["sensors"] = {name: Sensor(**sensor)
                               for name, sensor in sensors.items()}
        if anisotropy is not None:
            self["anisotropy"] = {name: Anisotropy(**data)
                                  for name, data in anisotropy.items()}

    @property
    def mesh_path(self):
        """Return the path to the `.msh` file of the model.

        Returns
        -------
        str
            The path to the `.msh` file of the model. If the model does not
            have a linked `.msh` file, return `None`.
        """
        mesh_path = self.get("mesh_path", None)
        if mesh_path is not None:
            return str(Path(self.path) / mesh_path)
        return None

    @property
    def tissues(self):
        """Return the tissues of the model.

        Returns
        -------
        dict[str: Tissue]
            The tissues of the model. If the model does not have any `Tissue`,
            return `None`.
        """
        return self.get("tissues", None)

    @property
    def sensors(self):
        """Return the sensors of the model.

        Returns
        -------
        dict[str: Sensor]
            The sensors of the model. If the model does not have any `Sensor`,
            return `None`.
        """
        return self.get("sensors", None)

    @property
    def anisotropy(self):
        """Return the anisotropy of the model.

        Returns
        -------
        dict[str: Anisotropy]
            The anisotropy of the model. If the model does not have any
            `Anisotropy`, return `None`.
        """
        return self.get("anisotropy", None)
