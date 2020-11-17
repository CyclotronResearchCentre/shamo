"""Implement `SolHDTDCSSim` class."""
from shamo.core.solutions.single import SolGetDP


class SolHDTDCSSim(SolGetDP):
    """Store information about a HD-tDCS simulation.

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
    references : list [str]
        The names of the references.
    source : list [str]
        The name of the electrode used as a source.
    current : float
        The injected current.
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        self.update(
            {
                "references": kwargs.get("references", []),
                "source": kwargs.get("source", []),
                "current": kwargs.get("current", 0.0),
            }
        )

    @property
    def references(self):
        """Return the names of the electrodes used as references.

        Returns
        -------
        list [str]
            The names of the electrodes used as references.
        """
        return self["references"]

    @property
    def source(self):
        """Return the name of the electrode used as source.

        Returns
        -------
        str
            The name of the electrode used as source.
        """
        return self["source"][0]

    @property
    def current(self):
        """Return the injected current.

        Returns
        -------
        float
            The injected current.
        """
        return self["current"]

    @property
    def v_pro_path(self):
        """Return the path to the PRO file containing the electric potential.

        Returns
        -------
        pathlib.Path
            The path to the PRO file containing the electric potential.
        """
        return self.path / f"{self.name}_v.pro"

    @property
    def j_pro_path(self):
        """Return the path to the PRO file containing the current density.

        Returns
        -------
        pathlib.Path
            The path to the PRO file containing the current density.
        """
        return self.path / f"{self.name}_j.pro"

    @property
    def mag_j_pro_path(self):
        """Return the path to the PRO file containing the norm of the current density.

        Returns
        -------
        pathlib.Path
            The path to the PRO file containing the norm of the current density.
        """
        return self.path / f"{self.name}_mag_j.pro"
