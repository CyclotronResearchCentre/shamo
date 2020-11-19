"""Implement the `ProbEEGLeadfield` class."""
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import gmsh
import h5py
import nibabel as nib
import numpy as np
from scipy.sparse import csc_matrix

from shamo.core.problems.single import (
    ProbGetDP,
    CompGridSampler,
    CompTissueProp,
    CompSensors,
    CompTissues,
)
from shamo.utils.onelab import read_vector_file, get_elems_coords, pos_to_nii
from .solution import SolEEGLeadfield

logger = logging.getLogger(__name__)


class ProbEEGLeadfield(ProbGetDP):
    """A problem definition to generate the EEG leadfield matrix.

    Attributes
    ----------
    sigmas : shamo.core.problems.single.CompTissueProp
        The electrical conductivity of the tissues.
    markers : shamo.core.problems.single.CompSensors
        The electrodes to ignore when solving the problem.
    reference : shamo.core.problems.single.CompSensors
        The electrode to use as the reference.
    rois : shamo.core.problems.single.CompTissues
        The tissues in which the leadfield must be computed.
    grid : shamo.core.problems.single.CompGridSampler
        The grid sampler if the source space must be based on a grid.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._source = CompSensors()
        self.markers = CompSensors()
        self.reference = CompSensors()
        self.rois = CompTissues()
        self.grid = CompGridSampler()

    @property
    def template(self):
        """Return the name of the template PRO file.

        Returns
        -------
        str
            The name of the template PRO file.
        """
        return "eeg_leadfield.tmplt"

    def solve(self, name, parent_path, model, **kwargs):
        """Solve the EEG forward problem and build the leadfield matrix.

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
        shamo.eeg.SolEEGLeadfield
            The EEG leafield object.
        """
        for n, t in model.tissues.items():
            self._vol.set(n, t.vol.group)
        sensors = list(model.sensors.keys())
        for s in sensors:
            if s not in self.reference["sensors"]:
                self._source["sensors"] = [s]
                break

        with TemporaryDirectory() as d:
            self._check_components(**model)
            sensors = self._gen_rhs(model, d)
            self._gen_pro_file(d, **kwargs, **model, active_sensors=sensors)
            self._run_getdp(model, d)
            src = Path(d) / f"{name}.hdf5"
            with h5py.File(src, "w") as f:
                for i, s in enumerate(sensors):
                    if i == 0:
                        row, source_sp = self._gen_row(i, d, model)
                        shape = (len(sensors), row.size)
                        data = f.create_dataset(
                            "e_field", shape, dtype="f", compression="lzf",
                        )
                    else:
                        row, _ = self._gen_row(i, d, model)
                    data[i, :] = row
            sol = SolEEGLeadfield(
                name,
                parent_path,
                markers=self.markers["sensors"],
                reference=self.reference["sensors"],
                rois=self.rois["tissues"],
                sensors=sensors,
                shape=shape,
                sigmas=self.sigmas,
                use_grid=self.grid.use_grid,
            )
            sol["model_json_path"] = str(sol.get_relative_path(model.json_path))
            Path.rename(src, sol.matrix_path)
            if self.grid.use_grid:
                source_sp.to_filename(sol.source_sp_path)
            else:
                np.savez(sol.source_sp_path, tags=source_sp[0], coords=source_sp[1])
            sol.save()
        return sol

    def _gen_row(self, i, tmp_dir, model):
        """Generate a single row of the leadfield matrix.

        Parameters
        ----------
        i : int
            The index of the row.
        tmp_dir : str, byte or os.PathLike
            The path to the temporary directory.
        model : shamo.FEM
            The finite element model.

        Returns
        -------
        numpy.ndarray
            The row of the matrix.
        source_sp : nibabel.Nifti1Image|tuple [numpy.ndarray]
            The source space.
        """
        tmp_dir = Path(tmp_dir)
        source_sp = None
        if self.grid.use_grid:
            img = self.grid.nii_from_pos(tmp_dir / f"{i}.pos", tmp_dir / f"{i}.nii")
            row = img.get_fdata()[self.grid.mask].ravel()
            if i == 0:
                source_sp = nib.Nifti1Image(
                    self.grid.mask.astype(np.uint8), self.grid.affine
                )
        else:
            elem_type, elems_tags, row = read_vector_file(tmp_dir / f"{i}.e")
            if i == 0:
                logger.info("Acquiring elements coordinates.")
                gmsh.initialize()
                gmsh.merge(str(model.mesh_path))
                coords = get_elems_coords(elem_type, elems_tags)
                gmsh.finalize()
                source_sp = (elems_tags, coords)
            row = row.ravel()
        return row, source_sp

    def _check_components(self, **kwargs):
        """Check if the components are properly set."""
        super()._check_components(**kwargs)
        self._source.check("source", **kwargs)
        self.reference.check("reference", **kwargs)
        self.rois.check("region of interest", **kwargs)
        self.grid.check("grid", **kwargs)

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
                "rois": self.rois.to_pro_param(**kwargs),
                "sources": self._source.to_pro_param(**kwargs),
                "sinks": self.reference.to_pro_param(**kwargs),
                "n_sensors": len(kwargs.get("active_sensors", {})) - 1,
                "use_grid": self.grid.to_pro_param(**kwargs),
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
                "rois": self.rois.to_py_param(**kwargs),
                "reference": self.reference.to_py_param(**kwargs),
                "markers": self.markers.to_py_param(**kwargs),
                "use_grid": self.grid.use_grid,
            }
        )
        if self.grid.use_grid:
            params["grid"] = self.grid.to_py_param(**kwargs)
        return params

    def _gen_rhs(self, model, tmp_dir):
        """Generate the right hand sides for the problem.

        Parameters
        ----------
        model : shamo.FEM
            The finite element model.
        tmp_dir : str, byte or os.PathLike
            The path to the temporary directory.

        Returns
        -------
        list [str]
            The names of the active sensors.
        """
        logger.info("Generating right hand sides.")
        gmsh.initialize()
        gmsh.open(str(model.mesh_path))
        n_nodes = gmsh.model.mesh.getNodes()[0].size
        gmsh.finalize()
        ref_row_idx = model.sensors[self.reference["sensors"][0]].node - 1
        sensors = []
        i = 0
        for n, s in model.sensors.items():
            if n not in self.reference["sensors"] and n not in self.markers["sensors"]:
                rhs = csc_matrix(
                    ((1, -1), ((s.node - 1, ref_row_idx), (0, 0))),
                    shape=(n_nodes, 1),
                    dtype=np.int,
                )
                np.savetxt(Path(tmp_dir) / f"{i}.rhs", rhs.toarray(), fmt="%d")
                sensors.append(n)
                i += 1
        return sensors
