"""API for `shamo.problem.forward.eeg`."""
from .eeg_forward_problem import EEGForwardProblem
from .eeg_leadfield_matrix import EEGLeadfieldMatrix

__all__ = ["EEGForwardProblem", "EEGLeadfieldMatrix"]
