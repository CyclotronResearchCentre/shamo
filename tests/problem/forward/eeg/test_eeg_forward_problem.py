from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from shamo.model import FEModel
from shamo.problem.forward.eeg import EEGForwardProblem, EEGLeadfieldMatrix


def test_solve():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/full_model")),
                        str(Path(parent_path) / "full_model"))
        model = FEModel.load(str(Path(parent_path)
                                 / "full_model/full_model.json"))
        problem = EEGForwardProblem()
        problem.add_tissue("a", 1.0)
        problem.add_tissue("b", 0.5, True)
        problem.add_tissue("c", 0.25, True)

        problem.set_reference("A")
        problem.add_markers(["C", "G"])
        problem.add_regions_of_interest(["b", "c"])
        leadfield = problem.solve(model, "leadfield", parent_path)
        assert(leadfield.shape == (5, 2103))


def test_load():
    leadfield = EEGLeadfieldMatrix.load(
        str(Path("tests/data/eeg_leadfield/eeg_leadfield.json")))
    assert(leadfield.shape == (5, 2103))
    assert(leadfield.n_sensors == 5)
    assert(leadfield.n_elements == 701)
    assert(leadfield.sensor_names == ["B", "D", "E", "F", "H"])
