"""Implement `ForwardProblem` class.

This module implements the `ForwardProblem` class which is the base for any
forward problem.
"""
import abc

from shamo.core import Problem
from .tissue_property import TissueProperty


class ForwardProblem(Problem):
    """The base for any forward problem.

    Parameters
    ----------
    regions_of_interest : list [str]
        The names of the regions of interest.
    markers : list [str]
        The names of the markers.
    electrical_conductivity : dict [str, dict]
        The electrical conductivity of the tissues [S/m].
    """

    def __init__(self, **kwargs):
        super().__init__()
        # Region of interest
        self["regions_of_interest"] = kwargs.get("regions_of_interest", [])
        # Markers
        self["markers"] = kwargs.get("markers", [])
        # Elcectrical conductivity
        electrical_conductivity = kwargs.get("electrical_conductivity", {})
        self["electrical_conductivity"] = {
            name: TissueProperty(**data)
            for name, data in electrical_conductivity.items()
        }

    @property
    def regions_of_interest(self):
        """Return the names of the regions of interest of the problem.

        Returns
        -------
        list [str]
            The names of the regions of interest of the problem.
        """
        return self["regions_of_interest"]

    @property
    def markers(self):
        """Return the names of the markers of the problem.

        Returns
        -------
        list [str]
            The names of the markers of the problem.
        """
        return self["markers"]

    @property
    def electrical_conductivity(self):
        """Return the electrical conductivity of the tissues [S/m].

        Returns
        -------
        dict[str, shamo.problem.forward.tissue_property.TissueProperty]
            The electrical conductivity of the tissues [S/m].
        """
        return self["electrical_conductivity"]

    def add_region_of_interest(self, name):
        """Add a region of interest to the problem.

        Parameters
        ----------
        name : str
            The name of the tissue.

        Returns
        -------
        shamo.problem.forward.forward_problem.ForwardProblem
            The problem.
        """
        self["regions_of_interest"].append(name)
        return self

    def add_regions_of_interest(self, names):
        """Add multiple regions of interest to the problem.

        Parameters
        ----------
        name : list [str]
            The names of the tissues.

        Returns
        -------
        shamo.problem.forward.forward_problem.ForwardProblem
            The problem.
        """
        self["regions_of_interest"].extend(names)
        return self

    def add_marker(self, name):
        """Add a marker to the problem.

        Parameters
        ----------
        name : str
            The name of the sensor.

        Returns
        -------
        shamo.problem.forward.forward_problem.ForwardProblem
            The problem.
        """
        self["markers"].append(name)
        return self

    def add_markers(self, names):
        """Add multiple markers to the problem.

        Parameters
        ----------
        name : list [str]
            The names of the sensors.

        Returns
        -------
        shamo.problem.forward.forward_problem.ForwardProblem
            The problem.
        """
        self["markers"].extend(names)
        return self

    def set_electrical_conductivity(self, name, value, anisotropy=""):
        """Set the electrical conductivity of a tissue.

        Parameters
        ----------
        name : str
            The name of the tissue.
        value : object
            The electrical conductivity [S/m].
        anisotropy : str, optional
            The name of the anisotropic field for this property. (The default
            is ``''``)

        Returns
        -------
        shamo.problem.forward.forward_problem.ForwardProblem
            The problem.
        """
        self["electrical_conductivity"][name] = TissueProperty(value, anisotropy)
        return self

    def set_electrical_conductivities(self, values, anistropies=None):
        """Set the electrical conductivity of a tissue.

        Parameters
        ----------
        name : str
            The name of the tissue.
        value : object
            The electrical conductivity of multiple tissues [S/m].
        anisotropy : dict [str, str], optional
            The names of the anisotropic fields for this property. (The default
            is ``None``)

        Returns
        -------
        shamo.problem.forward.forward_problem.ForwardProblem
            The problem.
        """
        if anistropies is None:
            anistropies = {}
        for name, value in values.items():
            anisotropy = anistropies.get(name, "")
            self.set_electrical_conductivity(name, value, anisotropy)
        return self

    def check_settings(self, model, **kwargs):
        """Check wether the current settings fit to the model.

        Parameters
        ----------
        model : shamo.model.fe_model.FEModel
            The model to check the settings for.

        Raises
        ------
        ValueError
            If none of the specified regions of interest can be found in the
            model.
            If ``is_roi_required`` is set to ``True`` and no region of interest
            is specified.
            If at least one tissue of the model has no specified electrical
            conductivity.

        Other Parameters
        ----------------
        is_roi_required : bool, optional
            If set to ``True``, at least one region of interest is required.
            (The defaul is ``False``)
        """
        is_roi_required = kwargs.get("is_roi_required", False)
        # Check region of interest
        if self.regions_of_interest:
            n_regions_of_interest = 0
            for region_of_interest in self.regions_of_interest:
                if region_of_interest in model.tissues:
                    n_regions_of_interest += 1
            if n_regions_of_interest == 0:
                raise ValueError(
                    (
                        "None of the specified regions of interest "
                        "can be found in the model."
                    )
                )
        elif is_roi_required and not self.regions_of_interest:
            raise ValueError("No specified region of interest.")
        # Check electrical conductivity
        for tissue in model.tissues:
            if tissue not in self.electrical_conductivity:
                raise ValueError(
                    (
                        "No electrical conductivity specified for "
                        "tissue with name '{}'."
                    ).format(tissue)
                )

    @abc.abstractmethod
    def solve(self, name, parent_path, model, **kwargs):
        """Solve the problem.

        Parameters
        ----------
        name : str
            The name of the solution.
        parent_path : PathLike
            The path to the parent directory of the solution.
        model : shamo.model.fe_model.FEModel
            The model to solve the problem on.

        Returns
        -------
        shamo.core.objects.FileObject
            The solution of the problem for the specified model.
        """
