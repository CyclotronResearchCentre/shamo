"""API for`shamo`."""
# Get rid of Gmsh warnings
import warnings

# Core
from .core.distribution import (
    ConstantDistribution,
    UniformDistribution,
    TruncatedNormalDistribution,
)

# Model
from .model.fe_model import FEModel
from .model.mesh_config import MeshConfig
from .model.sources.fe_source import FESource
from .model.sources.eeg_source import EEGSource

# Problems
from .problems.forward.eeg.eeg_forward_problem import EEGForwardProblem
from .problems.forward.eeg.eeg_simulation_problem import EEGSimulationProblem
from .problems.forward.eeg.eeg_parametric_forward_problem import (
    EEGParametricForwardProblem,
)

# Solutions
from .solutions.forward.eeg.eeg_forward_solution import EEGForwardSolution
from .solutions.forward.eeg.eeg_simulation_solution import EEGSimulationSolution
from .solutions.forward.eeg.eeg_parametric_forward_solution import (
    EEGParametricForwardSolution,
)

# Remove unnecessary warnings
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="A builtin ctypes object gave a PEP3118",
)
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message="divide by zero encountered in true_divide",
)
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, lineno=49, message="invalid value encountered in"
)

__all__ = [
    "ConstantDistribution",
    "UniformDistribution",
    "TruncatedNormalDistribution",
    "FEModel",
    "MeshConfig",
    "FESource",
    "EEGSource",
    "EEGForwardProblem",
    "EEGSimulationProblem",
    "EEGParametricForwardProblem",
    "EEGForwardSolution",
    "EEGSimulationSolution",
    "EEGParametricForwardSolution",
]
