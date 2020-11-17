"""API for `shamo.eeg`."""
from .leadfield.single.problem import ProbEEGLeadfield
from .leadfield.single.solution import SolEEGLeadfield

from .leadfield.parametric.problem import ProbParamEEGLeadfield
from .leadfield.parametric.solution import SolParamEEGLeadfield

__all__ = [
    "ProbEEGLeadfield",
    "SolEEGLeadfield",
    "ProbParamEEGLeadfield",
    "SolParamEEGLeadfield",
]
