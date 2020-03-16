"""API for`shamo`."""
# Get rid of Gmsh warnings
import warnings

# Model
from .model.fe_model import FEModel
from .model.mesh_config import MeshConfig
from .model.sources.fe_source import FESource
from .model.sources.eeg_source import EEGSource

# Problems
from .problems.forward.eeg.eeg_forward_problem import EEGForwardProblem
from .problems.forward.eeg.eeg_simulation_problem import EEGSimulationProblem

# Solutions
from .solutions.forward.eeg.eeg_forward_solution import EEGForwardSolution
from .solutions.forward.eeg.eeg_simulation_solution \
    import EEGSimulationSolution


warnings.filterwarnings("ignore", category=RuntimeWarning, lineno=523,
                        message="A builtin ctypes object gave a PEP3118")
__all__ = ["FEModel", "MeshConfig", "FESource", "EEGSource",
           "EEGForwardProblem", "EEGSimulationProblem", "EEGForwardSolution",
           "EEGSimulationSolution"]
