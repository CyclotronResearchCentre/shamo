"""API for `shamo.solutions`."""
from .forward.common_forward_solution import CommonForwardSolution
from .forward.forward_solution import ForwardSolution
from .forward.parametric_forward_solution import ParametricForwardSolution

__all__ = ["CommonForwardSolution", "ForwardSolution", "ParametricForwardSolution"]
