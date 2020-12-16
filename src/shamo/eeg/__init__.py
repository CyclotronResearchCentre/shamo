"""API for `shamo.eeg`."""
from .leadfield.single.problem import ProbEEGLeadfield
from .leadfield.single.solution import SolEEGLeadfield

from .leadfield.parametric.problem import ProbParamEEGLeadfield
from .leadfield.parametric.solution import SolParamEEGLeadfield
from .leadfield.parametric.surrogate import SurrEEGLeadfield, SurrEEGLeadfieldToRef

__all__ = [
    "ProbEEGLeadfield",
    "SolEEGLeadfield",
    "ProbParamEEGLeadfield",
    "SolParamEEGLeadfield",
    "SurrEEGLeadfield",
    "SurrEEGLeadfieldToRef",
]
