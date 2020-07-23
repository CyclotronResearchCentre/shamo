"""Implement `EEGSimulationProblem` class.

This module implements the `EEGSimulationProblem` class which provides a solver
for the EEG simulation problem.
"""
import os
from pathlib import Path
import re
import shutil
import subprocess as sp
from tempfile import TemporaryDirectory
from pkg_resources import resource_filename

import numpy as np

from .eeg_forward_problem import EEGForwardProblem
from shamo import EEGSource
from shamo.utils import TemplateFile


class EEGSimulationProblem(EEGForwardProblem):
    """Provide a solver for the EEG forward problem.

    Parameters
    ----------
    regions_of_interest : list [str]
        The names of the regions of interest.
    markers : list [str]
        The names of the markers.
    electrical_conductivity : dict [str, dict]
        The electrical conductivity of the tissues [S/m].
    reference : str
        The name of the reference sensor.

    See Also
    --------
    shamo.problems.forward.forward_problem.ForwardProblem
    """

    TEMPLATE_PATH = resource_filename(
        "shamo", str(Path("problems/forward/eeg/eeg_simulation_problem.pro"))
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Sources
        sources = kwargs.get("sources", [])
        self["sources"] = [EEGSource(**data) for data in sources]

    @property
    def sources(self):
        """Return the sources set for the problem.

        Returns
        -------
        list [shamo.model.sources.eeg_source.EEGSource]
            The sources set for the problem.
        """
        return self["sources"]

    def add_source(self, source):
        """Add a source to simulate.

        Parameters
        ----------
        source : shamo.model.sources.eeg_source.EEGSource
            The source to add.

        Returns
        -------
        shamo.problems.forward.eeg.eeg_simulation_problem.EEGSimulationProblem
            The problem.
        """
        self["sources"].append(source)
        return self

    def add_sources(self, sources):
        """Add multiple sources to simulate.

        Parameters
        ----------
        sources : list [shamo.model.sources.eeg_source.EEGSource]
            The sources to add.

        Returns
        -------
        shamo.problems.forward.eeg.eeg_simulation_problem.EEGSimulationProblem
            The problem.
        """
        self["sources"].extend(sources)
        return self

    def check_settings(self, model, **kwargs):
        """Check wether the current settings fit to the model.

        Parameters
        ----------
        model : shamo.FEModel
            The model to check the settings for.

        Raises
        ------
        ValueError
            If none of the specified regions of interest can be found in the
            model.
            If ``is_roi_required`` is set to ``True`` and no region of interest
            is specified.
            If at least one tissue of the model has no specified electrical
            conductivity.
            If a source do not exist in the model.
        """
        super().check_settings(model, **kwargs)
        for source in self.sources:
            if not model.source_exists(source):
                raise ValueError(
                    (
                        "Source located at '({:.3f}, {:.3f}, "
                        "{:.3f})' not defined in the "
                        "model."
                    ).format(*source.coordinates)
                )

    def solve(self, name, parent_path, model, **kwargs):
        """Solve the problem.

        Parameters
        ----------
        name : str
            The name of the solution.
        parent_path : PathLike
            The path to the parent directory of the solution.
        model : shamo.core.objects.FileObject
            The model to solve the problem on.

        Returns
        -------
        shamo.EEGSimulationSolution
            The solution of the problem for the specified model.
        """
        from shamo import EEGSimulationSolution

        self["regions_of_interest"] = [name for name in model.tissues]
        self.check_settings(model)
        # Initialize the solution
        solution = EEGSimulationSolution(name, parent_path)
        solution.set_problem(self)
        solution.set_model(model)
        # Generate recordings
        scratch_path = os.environ.get("SCRATCH_DIR", None)
        with TemporaryDirectory(dir=scratch_path) as temporary_path:
            # Generate problem file
            problem_path = str(Path(temporary_path) / "problem.pro")
            self._generate_problem_file(problem_path, model)
            # Solve problem
            command = [
                "getdp",
                problem_path,
                "-msh",
                model.mesh_path,
                "-solve",
                "Res_v",
                "-pos",
                "PostOp_v",
            ]
            try:
                sp.run(command, capture_output=True, check=True, cwd=temporary_path)
            except sp.CalledProcessError as exception:
                if exception.returncode != 1:
                    raise RuntimeError(
                        ("GetDP exit with code '{}' on command:" "\n'{}'").format(
                            exception.returncode, exception.stdout
                        )
                    )
            # Retrieve reference
            node_file_name = "v_skin.node"
            values = np.loadtxt(str(Path(temporary_path) / node_file_name), skiprows=1)
            sensor_index = np.where(values[:, 0] == model.sensors[self.reference].node)
            reference_value = values[sensor_index, 1]
            # Retrieve sensors recordings
            sensors = {
                name: sensor
                for name, sensor in model.sensors.items()
                if name not in self.markers and name != self.reference
            }
            recordings = {}
            for name, sensor in sensors.items():
                sensor_index = np.where(values[:, 0] == sensor.node)
                recordings[name] = float(values[sensor_index, 1] - reference_value)
            solution.set_recodings(recordings)
            # Apply reference to .pos files
            self._apply_reference_potential(
                Path(temporary_path) / "v.pos", reference_value
            )
            self._apply_reference_potential(
                Path(temporary_path) / "v_skin.pos", reference_value
            )
            # Save files
            file_names = ["j.pos", "v.pos", "v_skin.pos"]
            for file_name in file_names:
                shutil.copy(
                    Path(temporary_path) / file_name,
                    Path(solution.path) / "{}_{}".format(solution.name, file_name),
                )
        solution.save()
        return solution

    def _generate_problem_file(self, path, model):
        """Generate a ``.pro`` file with all the field filled.

        Parameters
        ----------
        path : PathLike
            The path to the output ``.pro`` file.
        model : shamo.model.fe_model.FEModel
            The model to fill the ``.pro`` file for.
        """
        path = str(Path(path))
        with TemplateFile(self.TEMPLATE_PATH, path) as template_file:
            # Add the regions
            tissue_regions = {
                name: tissue.volume_group for name, tissue in model.tissues.items()
            }
            template_file.replace_with_dict(
                "tissues",
                "region",
                tissue_regions,
                key_value_separator=" = Region[{",
                suffix="}];",
                separator="\n    ",
            )
            tissue_names = [tissue for tissue in tissue_regions]
            template_file.replace_with_list(
                "tissues", "name", tissue_names, separator=", "
            )
            # Add electrical conductivity
            all_parameters = {
                name: sigma.value
                for name, sigma in self.electrical_conductivity.items()
            }
            electrical_conductivity = {}
            for tissue in tissue_names:
                if self.electrical_conductivity[tissue].is_anisotropic:
                    anisotropy = self.electrical_conductivity[tissue].anisotropy
                    if anisotropy not in model.anisotropy:
                        raise ValueError(
                            (
                                "Anisotropic field with name '{}' "
                                "not found in "
                                "model."
                            ).format(anisotropy)
                        )
                    electrical_conductivity[tissue] = model.anisotropy[
                        anisotropy
                    ].generate_formula_text(**all_parameters)
                else:
                    electrical_conductivity[tissue] = str(
                        self.electrical_conductivity[tissue].value
                    )
            template_file.replace_with_dict(
                "tissues",
                "sigma",
                electrical_conductivity,
                key_value_separator="] = ",
                prefix="sigma[",
                suffix=";",
                separator="\n    ",
            )
            # Add sources
            source_regions = {}
            source_names = []
            source_currents = {}
            for i_source, source in enumerate(self.sources):
                model_source = model.get_source(source)
                for i_axis, value in enumerate(source.values):
                    if value != 0:
                        # First point
                        name = "Source_{}_{}_0".format(i_source, i_axis)
                        source_regions[name] = model_source.point_groups[i_axis][0]
                        source_names.append(name)
                        source_currents[name] = value / model_source.length
                        # Second point
                        name = "Source_{}_{}_1".format(i_source, i_axis)
                        source_regions[name] = model_source.point_groups[i_axis][1]
                        source_names.append(name)
                        source_currents[name] = -value / model_source.length
            template_file.replace_with_dict(
                "sources",
                "region",
                source_regions,
                key_value_separator=" = Region[{",
                suffix="}];",
                separator="\n    ",
            )
            template_file.replace_with_list(
                "sources", "name", source_names, separator=", "
            )
            template_file.replace_with_dict(
                "sources",
                "current",
                source_currents,
                key_value_separator="] = ",
                prefix="current[",
                suffix=";",
                separator="\n    ",
            )

    @staticmethod
    def _apply_reference_potential(path, reference_potential):
        """Subtract the reference value from all other measurements.

        Parameters
        ----------
        path : PathLike
            The path to the ``.pos`` file to edit.
        reference_potential : float
            The reference value.
        """
        new_content = []
        with open(path, "r") as pos_file:
            for i_line, line in enumerate(pos_file):
                if i_line > 0 and line != "};\n" and line != "":
                    parts = line.replace("){", ") {").split(" ")
                    values = [
                        float(match) - reference_potential
                        for match in re.findall(r"[\-\.\d]{2,}", parts[1])
                    ]
                    new_values = ",".join([str(value[0][0]) for value in values])
                    new_line = parts[0] + "{" + new_values + "};\n"
                    new_content.append(new_line)
                else:
                    new_content.append(line)
        with open(path, "w") as pos_file:
            pos_file.writelines(new_content)
