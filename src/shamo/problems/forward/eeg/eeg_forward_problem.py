"""Implement `EEGForwardProblem` class.

This module implements the `EEGForwardProblem` class which provides a solver
for the EEG forward problem.
"""
import os
from pathlib import Path
import subprocess as sp
from tempfile import TemporaryDirectory
from pkg_resources import resource_filename

import numpy as np
from scipy.sparse import csc_matrix
from scipy.spatial.distance import cdist

from shamo.problems import ForwardProblem
from shamo.utils import TemplateFile, get_elements_coordinates


class EEGForwardProblem(ForwardProblem):
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
    shamo.problems.ForwardProblem
    """

    TEMPLATE_PATH = resource_filename(
        "shamo", str(Path("problems/forward/eeg/eeg_forward_problem.pro"))
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Reference
        self["reference"] = kwargs.get("reference", "")

    @property
    def reference(self):
        """Return the name of the reference sensor.

        Returns
        -------
        str
            The name of the reference sensor.
        """
        return self["reference"]

    def set_reference(self, name):
        """Set the reference sensor.

        Parameters
        ----------
        name : str
            The name of the reference sensor.

        Returns
        -------
        shamo.problems.forward.eeg.eeg_forward_problem.EEGForwardProblem
            The problem.
        """
        self["reference"] = name
        return self

    def check_settings(self, model, **kwargs):
        """Check wether the current settings fit to the model.

        Parameters
        ----------
        model : shamo.model.fe_model.FEModel
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
        """
        super().check_settings(model, is_roi_required=True)
        # Check reference
        if self.reference not in model.sensors:
            raise ValueError(
                ("Missing reference sensor with name '{}' can be " "found.").format(
                    self.reference
                )
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

        Other Parameters
        ----------------
        min_source_dist : float, optional
            The minimum distance between two sources. If set to ``None``, all the
            elements of the region of interest are kept. Otherwise, equidistant elements
            are kept. (The default is ``None``)
        source_elems : dict [str, numpy.ndarray], optional
            A dictionary containing both the tags and the coordinates of the elements of
            the region of interest to keep. If set to ``None``, `min_source_dist` is
            used. Otherwise, `min_source_dist` is ignored. (The default is ``None``)

        Returns
        -------
        shamo.EEGForwardSolution
            The solution of the problem for the specified model.
        """
        from shamo import EEGForwardSolution

        self.check_settings(model)
        # Initialize the solution
        solution = EEGForwardSolution(name, parent_path)
        solution.set_problem(self)
        solution.set_model(model)
        # Generate matrix
        scratch_path = os.environ.get("SCRATCH_DIR", None)
        with TemporaryDirectory(dir=scratch_path) as temporary_path:
            # Get sensors and reference
            reference = model.sensors[self.reference]
            sensors = {
                name: sensor
                for name, sensor in model.sensors.items()
                if name not in self.markers and name != self.reference
            }
            n_sensors = len(sensors)
            # Generate right hand side files
            self._generate_rhs(model.n_nodes, sensors, reference, temporary_path)
            # Generate problem file
            problem_path = str(Path(temporary_path) / "problem.pro")
            self._generate_problem_file(problem_path, model, n_sensors)
            # Solve for each sensor
            command = [
                "getdp",
                problem_path,
                "-msh",
                model.mesh_path,
                "-solve",
                "resolution",
                "-pos",
                "post_operation",
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
            # Generate leadfield matrix
            matrix, element_types, element_tags = self._generate_matrix(
                sensors, temporary_path, solution.n_values_per_element
            )
            solution.set_sensors([name for name in sensors])
            # Generate element data
            element_coords = get_elements_coordinates(
                model, self.regions_of_interest, element_types, element_tags
            )
            # Reduce source density
            min_source_dist = kwargs.get("min_source_dist", None)
            source_elems = kwargs.get("source_elems", None)
            if min_source_dist is not None or source_elems is not None:
                if source_elems is None:
                    source_elems = self._reduce_source_density(
                        element_coords, element_tags, min_source_dist
                    )
                matrix = self._reduce_matrix(
                    matrix,
                    element_tags,
                    source_elems,
                    EEGForwardSolution.n_values_per_element,
                )
                element_tags = source_elems["tags"]
                element_coords = source_elems["coords"]
            solution.set_matrix(matrix)
            solution.set_elements(element_tags, element_coords)
        solution.save()
        return solution

    def _generate_problem_file(self, path, model, n_sensors):
        """Generate a ``.pro`` file with all the field filled.

        Parameters
        ----------
        path : PathLike
            The path to the output ``.pro`` file.
        model : shamo.model.fe_model.FEModel
            The model to fill the ``.pro`` file for.
        n_sensors : int
            The number of sensors to compute the solution for.
        """
        path = str(Path(path))
        with TemplateFile(self.TEMPLATE_PATH, path) as template_file:
            # Add the regions
            tissue_groups = {
                name: tissue.volume_group for name, tissue in model.tissues.items()
            }
            template_file.replace_with_dict(
                "region",
                "group",
                tissue_groups,
                key_value_separator=" = Region[{",
                suffix="}];",
                separator="\n    ",
            )
            tissue_names = [tissue for tissue in tissue_groups]
            template_file.replace_with_list(
                "name", "region", tissue_names, separator=", "
            )
            # Add region of interest
            regions_of_interest = [
                tissue for tissue in self.regions_of_interest if tissue in tissue_names
            ]
            template_file.replace_with_list(
                "name", "roi", regions_of_interest, separator=", "
            )
            # Add reference
            if self.reference not in model.sensors:
                raise ValueError(
                    ("Reference sensor '{}' not defined in " "model").format(
                        self.reference
                    )
                )
            template_file.replace_with_text(
                "tag", "sink", str(model.sensors[self.reference].group)
            )
            # Add source
            source_name = [
                sensor
                for sensor in model.sensors
                if sensor not in self.markers and sensor != self.reference
            ][0]
            template_file.replace_with_text(
                "tag", "source", str(model.sensors[source_name].group)
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
                "name",
                "sigma",
                electrical_conductivity,
                key_value_separator="] = ",
                prefix="sigma[",
                suffix=";",
                separator="\n    ",
            )
            # Set the number of sensors to compute for
            template_file.replace_with_text("count", "sensors", str(n_sensors - 1))

    @staticmethod
    def _generate_rhs(n_values, sensors, reference, out_path):
        """Generate the right hand sides.

        Parameters
        ----------
        n_values : int
            The length of the vector.
        sensors : dict [str, shamo.model.sensor.Sensor]
            The sensors to compute the solution for.
        reference : shamo.model.sensor.Sensor
            The sensor used as a reference.
        out_path : str
            The path to the directory where to create the files.
        """
        # Define values, rows and columns
        for i, (name, sensor) in enumerate(sensors.items()):
            values = [1, -1]
            row_indices = [sensor.node - 1, reference.node - 1]
            column_indices = [0, 0]
            b = csc_matrix(
                (values, (row_indices, column_indices)),
                shape=(n_values, 1),
                dtype=np.int,
            )
            b_path = Path(out_path) / "{}.b".format(i)
            np.savetxt(b_path, b.toarray(), fmt="%d")

    @staticmethod
    def _read_out_file(path):
        """Read one output file of the problem.

        Parameters
        ----------
        path : PathLike
            The path to the output file.

        Returns
        -------
        numpy.ndarray
            The element types.
        numpy.ndarray
            The element tags.
        numpy.ndarray
            The values.
        """
        data = np.loadtxt(
            path,
            dtype={
                "names": ("type", "tag", "x", "y", "z"),
                "formats": (np.uint8, np.uint, np.float, np.float, np.float),
            },
            usecols=(0, 1, -3, -2, -1),
        )
        return data["type"], data["tag"], np.vstack((data["x"], data["y"], data["z"])).T

    @staticmethod
    def _generate_matrix(sensors, path, n_values_per_element):
        """Generate the final matrix.

        Parameters
        ----------
        sensors : dict [str, shamo.model.sensor.Sensor]
            The sensors for which the matrix is computed.
        path : str
            The path were the solutions of the problem are stored.
        n_values_per_element : int
            The number of values recorded by element.

        Returns
        -------
        numpy.ndarray
            The generated matrix.
        numpy.ndarray
            The element types.
        numpy.ndarray
            The element tags.
        """
        matrix = None
        n_sensors = len(sensors)
        for i_sensor, name in enumerate(sensors):
            e_path = str(Path(path) / "{}.e".format(i_sensor))
            element_types, element_tags, values = EEGForwardProblem._read_out_file(
                e_path
            )
            if matrix is None:
                n_elements = element_tags.size
                matrix = np.empty(
                    (n_sensors, n_elements * n_values_per_element), dtype=np.float32
                )
            matrix[i_sensor, :] = values.flatten()
        return matrix, element_types, element_tags

    @staticmethod
    def _reduce_source_density(element_coords, element_tags, min_source_dist):
        """Remove unnecessary elements to reduce the size of the leadfield matrix.

        Parameters
        ----------
        element_coords : numpy.ndarray
            The coordinates of all the elements of the region of interest.
        element_tags : numpy.ndarray
            The tags of all the elements of the region of interest.
        min_source_dist : float
            Thee minimum distance between two sources.

        Returns
        -------
        dict [str, numpy.ndarray]
            A dictionary containing both the tags and the coordinates of the elements of
            the region of interest to keep.
        """
        init_size = element_tags.size
        used = []
        current_index = 0
        current_tag = element_tags[current_index]
        current_coords = element_coords[current_index]
        while len(used) != element_tags.size:
            # Compute distances
            distances = cdist([current_coords], element_coords).ravel()
            # Remove elements closer than min_source_dist
            min_index = np.where(
                np.logical_and(distances <= min_source_dist, distances != 0)
            )[0]
            element_coords = np.delete(element_coords, min_index, 0)
            element_tags = np.delete(element_tags, min_index)
            distances = np.delete(distances, min_index)
            # Set new current point
            used.append(current_tag)
            new_current_tag = current_tag
            current_dist = min_source_dist
            while np.isin(new_current_tag, used) and len(used) != element_tags.size:
                current_dist = np.min(distances[distances > current_dist])
                current_index = np.where(distances == current_dist)[0][0]
                new_current_tag = element_tags[current_index]
                current_coords = element_coords[current_index]
            current_tag = new_current_tag
        return {"tags": element_tags, "coords": element_coords}

    @staticmethod
    def _reduce_matrix(matrix, element_tags, source_elems, n_values_per_element):
        """Remove unnecessary columns from the leadfield matrix.

        Parameters
        ----------
        matrix : numpy.ndarray
            The full leadfield matrix.
        element_tags : numpy.ndarray
            The tags of all the elements of the region of interest.
        source_elems : dict [str, numpy.ndarray]
            A dictionary containing both the tags and the coordinates of the elements of
            the region of interest to keep.
        n_values_per_element : int
            The number of columns by element.

        Returns
        -------
        numpy.ndarray
            The reduced leadfield matrix.
        """
        source_tags = source_elems["tags"]
        mask = np.repeat(np.isin(element_tags, source_tags), n_values_per_element)
        return matrix[:, mask]
