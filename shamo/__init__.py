"""API for`shamo`."""
# Model
from .model.fe_model import FEModel
from .model.mesh_config import MeshConfig

# Problems
from .problems.forward.eeg.eeg_forward_problem import EEGForwardProblem

# Solutions
from .solutions.forward.eeg.eeg_forward_solution import EEGForwardSolution

__all__ = ["FEModel", "MeshConfig", "EEGForwardProblem", "EEGForwardSolution"]
