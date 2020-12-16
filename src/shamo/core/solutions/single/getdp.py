"""Implement the `SolGetDP` class."""
from pathlib import Path

from shamo.core.objects import ObjDir


class SolGetDP(ObjDir):
    """Store information about the solution of a `shamo.core.problems.single.ProbGetDP`.

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
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path)
        self.update(
            {
                "sigmas": kwargs.get("sigmas", {}),
                "model_json_path": kwargs.get("model_json_path", None),
            }
        )

    @property
    def sigmas(self):
        """Return the electrical conductivity of the tissues.

        Returns
        -------
        dict [str, list [float, str]]
            The electrical conductivity of the tissues.
        """
        return self["sigmas"]

    @property
    def model_json_path(self):
        """Return the path to the model JSON file.

        Returns
        -------
        pathlib.Path
            The path to the model JSON file.
        """
        return (self.path / self["model_json_path"]).resolve()
