from pathlib import Path
import struct
import subprocess as sp
from tempfile import TemporaryDirectory
from pkg_resources import resource_filename

import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import factorized

from shamo.problem.forward import ForwardProblem
from shamo.core import TemplateFile
from .eeg_leadfield_matrix import EEGLeadfieldMatrix


class EEGForwardProblem(ForwardProblem):
    """Allow generation of an EEG forward problem.

    Parameters
    ----------
    tissue_properties : dict[str: dict], optional
        A dictionary containing the name of the tissues as keys and their
        properties as values.

    parameters : dict[str: float | int], optional
        A dictionary containing the name of the parameters as keys and their
        values. (The default is `None`).

    region_of_interest : str | list[str], optional
        When string value is used, the region of interest is the tissue named
        after `region_of_interest`. When list value is used, the region of
        interest is the sum of all the tissues listed by their names. (The
        default is `None`).

    markers : list[str], optional
        A list of the names of the sensors which must not be added to the
        computation. (The default is `[]`).

    reference : str, optional
        The name of the sensor used as reference. (The default is `None`).

    Attributes
    ----------
    problem_type
    tissue_properties
    parameters
    region_of_interest
    markers
    reference

    See Also
    --------
    JSONObject
    """

    TEMPLATE_PATH = resource_filename("shamo", str(
        Path("problem/forward/eeg/eeg_forward_problem.pro")))

    def __init__(self, tissue_properties={}, parameters=None,
                 region_of_interest=None, markers=[], reference=None):
        super().__init__(ForwardProblem.EEG, tissue_properties, parameters,
                         region_of_interest)
        self["markers"] = markers
        if reference is not None:
            self["reference"] = reference

    @property
    def markers(self):
        """Return the names of the excluded sensors.

        Returns
        -------
        list[str]
            The names of the excluded sensors.
        """
        return self["markers"]

    @property
    def reference(self):
        """Return the name of the sensor used as a reference.

        Returns
        -------
        str
            The name of the sensor used as a reference. If the problem does not
            have any reference, return `None`.
        """
        return self.get("reference", None)

    def add_marker(self, name):
        """Add an excluded sensor to the problem.

        Parameters
        ----------
        name : str
            The name of the sensor to be excluded.

        Returns
        -------
        EEGForwardProblem
            The current problem.
        """
        if name not in self.markers:
            self["markers"].append(name)
        return self

    def add_markers(self, names):
        """Add multiple excluded sensors to the problem.

        Parameters
        ----------
        names : list[str]
            The names of the sensors to be excluded.

        Returns
        -------
        EEGForwardProblem
            The current problem.
        """
        for name in names:
            self.add_marker(name)
        return self

    def set_reference(self, name):
        """Set the sensor used as a reference for the problem.

        Parameters
        ----------
        name : str
            The name of the sensor to be used as a reference.

        Returns
        -------
        EEGForwardProblem
            The current problem.
        """
        self["reference"] = name
        return self

    def solve(self, model, name, parent_path, parents=True, exist_ok=True,
              **kwargs):
        """Solve the EEG forward problem and produce a leadfield matrix.

        Parameters
        ----------
        model : shamo.model.FEModel
            The model to solve the problem for.
        name : str
            The name given to the leadfield matrix.
        parent_path : str
            The path to the parent directory of the leadfield matrix.
        parents : bool, optional
            If set to `True`, any missing level in the tree is created. (The
            default is `True`).
        exist_ok : bool, optional
            If set to `True`, no exception is raised if the directory already
            exists. (The default is `True`).

        Other Parameters
        ----------------
        elements_path : str
            The path to a precomputed elements file.

        Returns
        -------
        shamo.problem.forward.eeg.EEGLeadfieldMatrix
            The generated leadfield matrix.

        Notes
        -----
        Solve the EEG forward problem using the reciprocity principle on an
        element basis.
        """
        # Check arguments
        for tissue in model.tissues.keys():
            if tissue not in self.tissue_properties:
                raise ValueError(("Missing tissue properties for "
                                  "tissue '{}'.").format(tissue))
        elements_path = kwargs.get("elements_path", None)
        # Initialize the leadfield matrix
        leadfield = EEGLeadfieldMatrix(name, parent_path, parents, exist_ok,
                                       settings=self)
        leadfield.set_model(model)
        # Solve
        with TemporaryDirectory() as temporary_path:
            # Generate problem file
            problem_path = str(Path(temporary_path) / "problem.pro")
            self._generate_problem_file(problem_path, model)
            left_hand_side = self._generate_left_hand_side(problem_path,
                                                           model.mesh_path)
            all_element_types, all_elements, matrix, sensors = \
                self._generate_matrix(
                    model, problem_path, left_hand_side)
            leadfield.set_sensor_names(sensors)
        # Undersample if needed
        if self.undersampling_distance != 0 or elements_path is not None:
            if elements_path is None:
                all_coordinates, undersampling_elements, \
                    undersampling_coordinates = \
                    self.get_undersampling_elements(
                        model, all_element_types, all_elements)
                leadfield.set_elements(undersampling_elements,
                                       undersampling_coordinates,
                                       all_elements, all_coordinates)
            else:
                leadfield.set_elements_path(elements_path)
                undersampling_elements, _, all_elements, _ = \
                    leadfield.get_elements(all=True)
            if all_elements is not None:
                matrix = self.undersample_matrix(
                    matrix, leadfield.N_VALUES_PER_ELEMENT,
                    np.array(all_elements), undersampling_elements)
        # Otherwise get all the coordinates of the elements
        else:
            all_coordinates = self.get_elements_coordinates(
                model, all_element_types, all_elements)
            leadfield.set_elements(all_elements, all_coordinates)
        leadfield.set_matrix(matrix)
        leadfield.save()
        return leadfield

    def _generate_problem_file(self, path, model):
        with TemplateFile(self.TEMPLATE_PATH, path) as template_file:
            # Add the regions
            tissue_groups = {name: tissue.volume_group
                             for name, tissue in model.tissues.items()}
            template_file.replace_with_dict("region", "group", tissue_groups,
                                            key_value_separator=" = Region[{",
                                            suffix="}];", separator="\n    ")
            tissue_names = [tissue for tissue in tissue_groups.keys()]
            template_file.replace_with_list("name", "region", tissue_names,
                                            separator=", ")
            # Add region of interest
            regions_of_interest = [tissue for tissue in self.region_of_interest
                                   if tissue in tissue_names]
            template_file.replace_with_list("name", "roi", regions_of_interest,
                                            separator=", ")
            # Add sigma
            tissue_sigmas = {}
            for tissue in tissue_names:
                if self.tissue_properties[tissue].use_anisotropy:
                    if tissue in model.anisotropy:
                        tissue_sigmas[tissue] = \
                            model.anisotropy[tissue].generate_sigma_text()
                    else:
                        tissue_sigmas[tissue] = \
                            str(self.tissue_properties[tissue].sigma)
                else:
                    tissue_sigmas[tissue] = \
                        str(self.tissue_properties[tissue].sigma)
            template_file.replace_with_dict("name", "sigma", tissue_sigmas,
                                            key_value_separator="] = ",
                                            prefix="sigma[", suffix=";",
                                            separator="\n    ")
            # Add reference
            if self.reference not in model.sensors:
                raise ValueError(("Reference sensor '{}' not defined in "
                                  "model").format(self.reference))
            template_file.replace_with_text(
                "tag", "sink", str(model.sensors[self.reference].group))
            # Add source
            source_name = [sensor for sensor in model.sensors.keys()
                           if sensor not in self.markers
                           and sensor != self.reference][0]
            template_file.replace_with_text(
                "tag", "source", str(model.sensors[source_name].group))

    @staticmethod
    def _generate_left_hand_side(problem_path, mesh_path):
        # Use Getdp
        command = ["getdp", problem_path, "-msh", mesh_path, "-solve",
                   "resolution"]
        sp.run(command, stdout=sp.PIPE)
        matrix_path = str(Path(problem_path).parent / "file_mat_system.m.bin")
        # Read matrix from file
        with open(matrix_path, "rb") as matrix_file:
            data = matrix_file.read()
        # Get shape and number of non-zero elements
        shape = struct.unpack(">ii", data[4:12])
        n_non_zero_values = struct.unpack(">i", data[12:16])[0]
        # read data
        offset = 16
        length = shape[1] * 4
        format = ">" + "i" * shape[1]
        values_per_row = struct.unpack(format, data[offset:offset+length])
        row_indices = [row for row, n in enumerate(values_per_row)
                       for i in range(n)]
        length = 8 * 2 * n_non_zero_values
        format = ">" + "d" * 2 * n_non_zero_values
        non_zero_values = struct.unpack(format, data[-length:])[::2]
        offset = length
        length = 4 * n_non_zero_values
        format = ">" + "i" * n_non_zero_values
        column_indices = list(struct.unpack(format,
                                            data[-offset-length:-offset]))
        left_hand_side = csc_matrix((non_zero_values,
                                     (row_indices, column_indices)), shape)
        return left_hand_side

    def _generate_matrix(self, model, problem_path, left_hand_side):
        header = ("$ResFormat /* GetDP 3.1.0, ascii */\n"
                  "1.1 0\n"
                  "$EndResFormat\n"
                  "$Solution  /* DofData #0 */\n"
                  "0 0 0 0")
        footer = "$EndSolution"
        e_path = str(Path(problem_path).parent / "e.out")
        sensors = {name: sensor for name, sensor in model.sensors.items()
                   if name not in self.markers}
        reference = sensors.pop(self.reference)
        solve = factorized(left_hand_side)
        matrix = None
        for i, (name, sensor) in enumerate(sensors.items()):
            # Generate vector b
            right_hand_side = np.zeros((left_hand_side.shape[1], 1))
            right_hand_side[sensor.node - 1] = -1
            right_hand_side[reference.node - 1] = 1
            # Compute the electric field
            solution = solve(right_hand_side)
            res = np.zeros((solution.shape[0], 2))
            res[:, 0] = solution[:, 0]
            res_path = str(Path(problem_path).parent / "{}.res".format(name))
            np.savetxt(res_path, res, fmt="%1.8f %i", header=header,
                       footer=footer, comments="")
            command = ["getdp", problem_path, "-msh", model.mesh_path, "-res",
                       res_path, "-pos", "post_operation"]
            sp.run(command, stdout=sp.PIPE)
            element_types, elements, values = self._read_out_file(e_path)
            Path(e_path).unlink()
            Path(res_path).unlink()
            if matrix is None:
                n_sensors = len(sensors)
                n_elements = elements.size
                matrix = np.empty((n_sensors, n_elements * 3),
                                  dtype=np.float32)
            matrix[i, :] = values.flatten()
        return element_types, elements, matrix, list(sensors.keys())

    @staticmethod
    def _read_out_file(path):
        element_types = []
        elements = []
        values = []
        with open(path, "rb") as out_file:
            for line in out_file:
                split = line.split()
                element = int(split[1])
                element_type = int(split[0])
                if element not in elements:
                    element_types.append(element_type)
                    elements.append(element)
                    values.append([float(v) for v in split[-3:]])
        return (np.array(element_types).flatten(),
                np.array(elements).flatten(),
                np.array(values))
