"""Implement `ProbHDTDCSSim` class."""
from pathlib import Path
from tempfile import TemporaryDirectory

import nibabel as nib

from shamo.core.problems.single import ProbGetDP, CompSensors, CompGridSampler
from shamo.utils.onelab import pos_to_nii
from .solution import SolHDTDCSSim


class ProbHDTDCSSim(ProbGetDP):
    """A problem definition to simulate HD-tDCS.

    Attributes
    ----------
    sigmas : shamo.core.problems.single.CompTissueProp
        The electrical conductivity of the tissues.
    references : shamo.core.problems.single.CompSensors
        The electrodes to use as the references.
    source : shamo.core.problems.single.CompSensors
        The electrode to use as the source.
    current : float
        The injected current.
    grid : shamo.core.problems.single.CompGridSampler
        The grid sampler if the source space must be based on a grid.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid = CompGridSampler()
        self.references = CompSensors()
        self.source = CompSensors()
        self.current = 1.0

    @property
    def template(self):
        """Return the name of the template PRO file.

        Returns
        -------
        str
            The name of the template PRO file.
        """
        return "hdtdcs_simulation.tmplt"

    def solve(self, name, parent_path, model, **kwargs):
        """Simulate HD-tDCS.

        Parameters
        ----------
        name : str
            The name of the solution.
        parent_path : str, byte or os.PathLike
            The path to the parent directory of the solution.
        model : shamo.fem.FEM
            The finite element model to solve the problem for.

        Returns
        -------
        shamo.hd_tdcs.SolHDTDCSSim
            The simulation results.
        """
        for n, t in model.tissues.items():
            self._vol.set(n, t.vol.group)
        shape = [int(s / 10) for s in model.shape]

        with TemporaryDirectory() as d:
            self._check_components(**model)
            self._gen_pro_file(d, **kwargs, **model)
            self._run_getdp(model, d)
            sol = SolHDTDCSSim(
                name,
                parent_path,
                source=self.source["sensors"],
                references=self.references["sensors"],
                sigmas=self.sigmas,
                current=self.current,
            )
            sol["model_json_path"] = str(sol.get_relative_path(model.json_path))
            for p in Path(d).iterdir():
                if p.suffix == ".pos":
                    if self.grid.use_grid:
                        self.grid.nii_from_pos(p, sol.path / f"{name}_{p.stem}.nii")
                    p.rename(sol.path / f"{name}_{p.name}")
            sol.save()
        return sol

    def _check_components(self, **kwargs):
        """Check if the components are properly set."""
        super()._check_components(**kwargs)
        self.grid.check("grid", **kwargs)
        self.source.check("source", **kwargs)
        self.references.check("references", **kwargs)

    def _prepare_pro_file_params(self, **kwargs):
        """Return the parameters required to generate the PRO file.

        Returns
        -------
        dict [str, ...]
            The parameters required to generate the PRO file.
        """
        params = super()._prepare_pro_file_params(**kwargs)
        params.update(
            {
                "use_grid": self.grid.to_pro_param(**kwargs),
                "sources": self.source.to_pro_param(**kwargs),
                "sinks": self.references.to_pro_param(**kwargs),
                "current": self.current,
            }
        )
        return params

    def _prepare_py_file_params(self, **kwargs):
        """Return the parameters required to generate the PY file.

        Returns
        -------
        dict [str, ...]
            The parameters required to generate the PY file.
        """
        params = super()._prepare_py_file_params(**kwargs)
        params.update(
            {
                "source": self.source.to_py_param(**kwargs),
                "references": self.references.to_py_param(**kwargs),
                "current": self.current,
                "use_grid": self.grid.use_grid,
            }
        )
        if self.grid.use_grid:
            params["grid"] = self.grid.to_py_param(**kwargs)
        return params
