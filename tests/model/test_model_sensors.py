from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

import numpy as np
import gmsh

from shamo import FEModel

MODEL_PATH = str(Path("tests/data/model_1"))


def _check_model_sensors(model, sensors):
    # Check structure
    assert(Path(model.path).exists())
    assert(Path(model.json_path).exists())
    assert(Path(model.mesh_path).exists())
    # Check model attributes
    gmsh.initialize()
    gmsh.open(model.mesh_path)
    groups = gmsh.model.getPhysicalGroups(0)
    entities = [gmsh.model.getEntitiesForPhysicalGroup(0, group)
                for dim, group in groups]
    nodes = [gmsh.model.mesh.getNodes(0, np.array(entity).astype(np.int))[0][0]
             for entity in entities]
    mesh_coords = [tuple(gmsh.model.mesh.getNodes(0, entity)[1][:3])
                   for entity in entities]
    points = {gmsh.model.getPhysicalName(*group): {
        "group": group[1], "entity": entities[i], "node": nodes[i],
        "coords": mesh_coords[i]}
        for i, group in enumerate(groups)}
    for name, coords in sensors.items():
        assert(name in model.sensors)
        assert(name in points)
        assert(model.sensors[name].real_coordinates
               == tuple([c / 1000 for c in coords]))
        assert(model.sensors[name].mesh_coordinates == points[name]["coords"])
        assert(model.sensors[name].group == points[name]["group"])
        assert(model.sensors[name].entity == points[name]["entity"])
        assert(model.sensors[name].node == points[name]["node"])
    gmsh.finalize()


def test_add_sensor():
    with TemporaryDirectory() as parent_path:
        # Load model
        shutil.copytree(MODEL_PATH, str(Path(parent_path) / "model_1"))
        model_path = str(Path(parent_path) / "model_1/model_1.json")
        model = FEModel.load(model_path)
        # Add sensor
        coordinates = [(x, y, z) for x in (0, 10) for y in (0, 10)
                       for z in (0, 10)]
        sensors = {chr(ord("A") + i): c for i, c in enumerate(coordinates)}
        for name, coords in sensors.items():
            model.add_sensor(name, coords, "a")
        model.save()
        # Test the model
        _check_model_sensors(model, sensors)


def test_add_sensors():
    with TemporaryDirectory() as parent_path:
        # Load model
        shutil.copytree(MODEL_PATH, str(Path(parent_path) / "model_1"))
        model_path = str(Path(parent_path) / "model_1/model_1.json")
        model = FEModel.load(model_path)
        # Add sensor
        coordinates = [(x, y, z) for x in (0, 10) for y in (0, 10)
                       for z in (0, 10)]
        sensors = {chr(ord("A") + i): c for i, c in enumerate(coordinates)}
        model.add_sensors(sensors, "a")
        model.save()
        # Test the model
        _check_model_sensors(model, sensors)
