"""Implement the `CompTissueProp` class."""
import logging

from .abc import CompABC

logger = logging.getLogger(__name__)


class CompTissueProp(CompABC):
    """Store information about a tissue property."""

    def check(self, name, **kwargs):
        """Check if the tissue property is properly set.

        Parameters
        ----------
        name : str
            The name of the property.

        Raises
        ------
        RuntimeError
            If no property is set for an existing tissue.
            If a field set for a tissue does not exist.

        Other Parameters
        ----------------
        tissues : dict [str, shamo.Tissue]
            The tissues of the model.
        """
        logger.info(f"Checking tissue property '{name}'.")
        tissues = kwargs.get("tissues", {})
        for t in tissues.keys():
            if t not in self:
                raise RuntimeError(f"No property value for tissue '{t}'.")
        for t, p in self.items():
            if p[1] is not None and p[1] not in tissues[t].fields:
                raise RuntimeError(f"No field '{p[1]}' in tissue '{t}'.")

    def to_pro_param(self, name="", **kwargs):
        """Return the parameters required to generate the PRO file.

        Parameters
        ----------
        name : str
            The name of the property.

        Returns
        -------
        list [dict [str, float|str]]
            The tissue properties.

        Other Parameters
        ----------------
        tissues : dict [str, shamo.Tissue]
            The tissues of the model.

        Notes
        -----
        If a field was set for the property of a tissue, its formula is fed with all the
        named parameters and evaluated to produce the expression.
        """
        params = []
        tissues = kwargs.get("tissues", {})
        prop = {name: {t: p[0] for t, p in self.items()}}
        for t, p in self.items():
            if p[1] is None:
                params.append({"tissue": t, "prop": p[0]})
            else:
                params.append(
                    {
                        "tissue": t,
                        "prop": tissues[t].fields[p[1]].gen_formula(**prop, **kwargs),
                    }
                )
        return params

    def to_py_param(self, **kwargs):
        """Return the parameters required to generate the PY file.

        Returns
        -------
        list [dict [str, str|float]]
            The tissue properties.

        Notes
        -----
        Each element of the list is formatted as ``{"tissue": name, "prop": value,
        "field": field_name}``.
        """
        return [{"tissue": t, "prop": p[0], "field": p[1]} for t, p in self.items()]

    def set(self, tissue, prop, field=None):
        """Set the property for a tissue.

        Parameters
        ----------
        tissue : str
            The name of the tissue.
        prop : float
            The value of the property.
        field : str, optional
            The name of the field associated.
        """
        self[tissue] = [prop, field]

    def sets(self, props):
        """Set multiple properties at once.

        Parameters
        ----------
        props : dict [str, float]
            The properties of the tissues.
        """
        for t, p in props.items():
            self[t] = [p, None]
