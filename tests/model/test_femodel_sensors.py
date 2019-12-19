from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from shamo.model import FEModel


def test_add_sensor_on_tissue():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        model.add_sensor_on_tissue("A", (0, 0, 0), "a")
        assert("A" in model.sensors)
        assert(model.sensors["A"].coordinates_error < 1)


def test_add_sensors_on_tissue():
    with TemporaryDirectory() as parent_path:
        shutil.copytree(str(Path("tests/data/only_geometry")),
                        str(Path(parent_path) / "only_geometry"))
        model = FEModel.load(str(Path(parent_path)
                                 / "only_geometry/only_geometry.json"))
        sensors_coordinates = {"A": (0, 0, 0), "B": (10, 10, 10)}
        model.add_sensors_on_tissue(sensors_coordinates, "a")
        assert("A" in model.sensors)
        assert(model.sensors["A"].coordinates_error < 1)
        assert("B" in model.sensors)
        assert(model.sensors["B"].coordinates_error < 1)
