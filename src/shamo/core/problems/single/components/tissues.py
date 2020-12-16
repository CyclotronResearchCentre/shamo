"""Implement the `CompTissues` class."""
import logging

from .abc import CompABC

logger = logging.getLogger(__name__)


class CompTissues(CompABC):
    """Store information about a list of tissues.

    Other Parameters
    ----------------
    tissues : list [str]
        The list of tissue names.
    """

    def __init__(self, **kwargs):
        super().__init__(tissues=kwargs.get("tissues", []))

    def check(self, name, **kwargs):
        """Check if the list of tissues is properly set.

        Parameters
        ----------
        name : str
            The name of the list of tissue names.

        Raises
        ------
        RuntimeError
            If a tissue does not exist in the model.

        Other Parameters
        ----------------
        tissues : dict [str, shamo.Tissue]
            The tissues of the model.
        """
        logger.info(f"Checking tissues '{name}'.")
        tissues = kwargs.get("tissues", {})
        for t in self["tissues"]:
            if t not in tissues:
                raise RuntimeError(f"Tissue '{t}' not found in model.")

    def to_pro_param(self, **kwargs):
        """Return the parameters required to generate the PRO file.

        Returns
        -------
        list [dict [str, int]]
            The list of physical groups of the tissues.

        Other Parameters
        ----------------
        tissues : dict [str, shamo.Tissue]
            The tissues of the model.
        """
        tissues = kwargs.get("tissues", {})
        return [{"tissue": tissues[t].vol.group} for t in self["tissues"]]

    def to_py_param(self, **kwargs):
        """Return the parameters required to generate the PY file.

        Returns
        -------
        list [str]
            The list of tissue names.
        """
        return self["tissues"]

    def add(self, tissue):
        """Add a tissue to the list.

        Parameters
        ----------
        tissue : str
            The name of the tissue.
        """
        self["tissues"].append(tissue)

    def adds(self, tissues):
        """Add multiple tissues to the list.

        Parameters
        ----------
        tissues : list [str]
            The names of the tissues.
        """
        self["tissues"].extend(tissues)
