"""API for `shamo.eeg`."""
from .leadfield.single.problem import ProbEEGLeadfield
from .leadfield.single.solution import SolEEGLeadfield


__all__ = ["ProbEEGLeadfield", "SolEEGLeadfield"]
