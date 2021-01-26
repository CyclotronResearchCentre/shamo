"""API for `shamo.hd_tdcs`."""
from .simulation.single.problem import ProbHDTDCSSim
from .simulation.single.solution import SolHDTDCSSim

from .simulation.parametric.problem import ProbParamHDTDCSSim
from .simulation.parametric.solution import SolParamHDTDCSSim
from .simulation.parametric.surrogate import (
    SurrMaskedScalarNiiJ,
    SurrMaskedScalarNiiMagJ,
    SurrMaskedScalarNiiV,
)


__all__ = [
    "ProbHDTDCSSim",
    "SolHDTDCSSim",
    "ProbParamHDTDCSSim",
    "SolParamHDTDCSSim",
    "SurrMaskedScalarNiiJ",
    "SurrMaskedScalarNiiMagJ",
    "SurrMaskedScalarNiiV",
]
