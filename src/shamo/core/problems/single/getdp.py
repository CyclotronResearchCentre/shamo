"""Implement the `ProbGetDP` class."""
from abc import abstractproperty, abstractmethod
import logging
from pathlib import Path
import re
from subprocess import CalledProcessError, Popen, PIPE, STDOUT

from jinja2 import Environment, PackageLoader
import numpy as np

from .abc import ProbABC
from .components.tissue_property import CompTissueProp
from shamo.utils.logging import subprocess_to_logger
from shamo.utils.onelab import LOG_PATTERN

logger = logging.getLogger(__name__)


class ProbGetDP(ProbABC):
    """A base class for any GetDP problem.

    Attributes
    ----------
    sigmas : shamo.core.problems.single.CompTissueProp
        The electrical conductivity of the tissues.

    See Also
    --------
    shamo.core.problems.single.ProbABC
    """

    def __init__(self, **kwargs):
        self._vol = CompTissueProp()
        self.sigmas = CompTissueProp()

    @abstractproperty
    def template(self):
        """Return the name of the template PRO file.

        Returns
        -------
        str
            The name of the template PRO file.
        """

    def _prepare_pro_file_params(self, **kwargs):
        """Return a dict filled with all the required parameters to generate a PY file.

        Returns
        -------
        dict [str, Any]
            The dict filled with all the required parameters.
        """
        return {
            "vol": self._vol.to_pro_param(**kwargs),
            "sigmas": self.sigmas.to_pro_param(name="sigma", **kwargs),
        }

    def _check_components(self, **kwargs):
        """Check if all the components are properly set."""
        self._vol.check("regions", **kwargs)
        self.sigmas.check("sigmas", **kwargs)

    @abstractmethod
    def _prepare_py_file_params(self, **kwargs):
        """Return a dict filled with all the required parameters to generate a PRO file.

        Returns
        -------
        dict [str, Any]
            The dict filled with all the required parameters.
        """
        return {"sigmas": self.sigmas.to_py_param(**kwargs)}

    def _gen_pro_file(self, tmp_dir, **kwargs):
        """Generate the PRO file based on the template.

        Parameters
        ----------
        tmp_dir : str, byte or os.PathLike
            The path to the directory the PRO file must be created in.
        """
        logger.info("Generating problem file.")
        env = Environment(loader=PackageLoader("shamo", "templates/pro"))
        template = env.get_template(self.template)
        content = template.render(**self._prepare_pro_file_params(**kwargs))
        logger.debug(content)
        with open(Path(tmp_dir) / "problem.pro", "w") as f:
            f.write(content)

    def _run_getdp(self, model, tmp_dir):
        """Run GetDP to solve the PRO file.

        Parameters
        ----------
        model : shamo.fem.FEM
            The model to solve the problem for.
        tmp_dir : str, byte or os.PathLike
            The path to the directory the PRO file must be created in.

        Raises
        ------
        CalledProcessError
            If GetDP exits with a wrong exit code.
        """
        cmd = [
            "getdp",
            "problem.pro",
            "-msh",
            str(model.mesh_path.resolve()),
            "-solve",
            "res",
            "-bin",
            "-v2",
        ]
        logger.info(f"Running GetDP with command: {' '.join(cmd)}")
        process = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=tmp_dir)
        exitcode = subprocess_to_logger(process, logger, logging.INFO, LOG_PATTERN)
        if exitcode != 0:
            raise CalledProcessError(exitcode, cmd)
