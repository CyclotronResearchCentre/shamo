"""Implement `SolParamGetDP` class."""
from .abc import SolParamABC
from shamo.core.distributions import DistABC


class SolParamGetDP(SolParamABC):
    """Store information about the solution of a parametric problem depending on Getdp.

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

    See Also
    --------
    shamo.core.solutions.parametric.SolParamABC
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        self.update(
            {
                "sigmas": {
                    t: [DistABC.load(**p[0]), p[1]]
                    for t, p in kwargs.get("sigmas", {}).items()
                },
                "model_json_path": kwargs.get("model_json_path", None),
            }
        )

    @property
    def sigmas(self):
        """Return the electrical conductivity of the tissues.

        Returns
        -------
        dict [str, list [shamo.DistABC, str]]
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
