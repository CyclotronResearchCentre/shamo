"""Implement `SolParamHDTDCSSim` class."""
from shamo.core.solutions.parametric import SolParamGetDP
from shamo.hd_tdcs import SolHDTDCSSim
from shamo import DistConstant


class SolParamHDTDCSSim(SolParamGetDP):
    """Store information about a HD-tDCS simulation.

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
    references : list [str]
        The names of the references.
    source : list [str]
        The name of the electrode used as a source.
    current : shamo.DistABC
        The injected current.
    """

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        self.update(
            {
                "references": kwargs.get("references", []),
                "source": kwargs.get("source", []),
                "current": kwargs.get("current", DistConstant(0.0)),
            }
        )

    @property
    def sub_class(self):
        return SolHDTDCSSim

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
        shamo.DistABC
            The injected current.
        """
        return self["current"]

    def finalize(self, **kwargs):
        """Finalize the solution."""
        self._get_sub_json_paths()
        self.save()
