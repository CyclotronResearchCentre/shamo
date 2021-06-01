"""API for `shamo`."""
import warnings

from shamo.core.distributions import *
from shamo.core.fem import *

__version__ = "1.1.1"

# Remove unnecessary warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, lineno=521)
