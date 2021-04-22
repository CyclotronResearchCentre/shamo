"""Implement `CompParamTissueProp` class."""
from shamo.core.distributions import DistABC
from shamo.core.problems.single import CompTissueProp


class CompParamTissueProp(CompTissueProp):
    """Store information about a random tissue property."""

    def to_param(self, name="", **kwargs):
        """Return the fixed and varying parameters separately.

        Parameters
        ----------
        name : str
            The name of the property.

        Returns
        -------
        list [list [str, list [float, str | None]]]
            The fixed parameters.
        list [list [str, list [shamo.DistABC, str | None]]]
            The varying parameters.
        """
        fixed = []
        varying = []
        for t, p in self.items():
            if name != "":
                t = f"{name}.{t}"
            if p[0].dist_type == DistABC.TYPE_CONSTANT:
                fixed.append([t, [p[0].val, p[1]]])
            else:
                varying.append([t, p])
        return fixed, varying
