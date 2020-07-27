"""Implement `EEGSimulationSolution` class.

This module implements the `EEGSimulationSolution` class which holds the data
corresponding to the solution of the EEG simulation problem.
"""
from shamo.core import Solution


class EEGSimulationSolution(Solution):
    """The base to an EEG simulation problem.

    Parameters
    ----------
    name : str
        The name of the solution.
    parent_path : PathLike
        The path to the parent directory of the solution.

    Other Parameters
    ----------------
    problem : dict [str, Any]
        The problem that result in this solution.
    recordings : dict [str, float]
        The recordings of the sensors [V].

    See Also
    --------
    shamo.core.solution.Solution
    """

    from shamo import EEGSimulationProblem

    PROBLEM_FACTORY = EEGSimulationProblem

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        # Recordings
        self["recordings"] = kwargs.get("recordings", {})

    @property
    def recordings(self):
        """Return the recordings of the sensors [V].

        Returns
        -------
        dict [str, float]
            The recordings of the sensors [V].
        """
        return self["recordings"]

    def set_recodings(self, recordings):
        """Set the recordings of the sensors.

        Parameters
        ----------
        recordings : dict [str, float]
            The recordings of the sensors [V].

        Returns
        -------
        shamo.EEGSimulationSolution
            The solution.
        """
        self["recordings"] = {name: float(value) for name, value in recordings.items()}
        return self
