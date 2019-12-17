import json
from pathlib import Path
from tempfile import TemporaryDirectory

from shamo.core import JSONObject


def test_init():
    name = "test_object"
    with TemporaryDirectory() as parent_path:
        json_object = JSONObject(name, parent_path)
        object_path = Path(parent_path) / name
        assert(object_path.exists())
        assert(object_path.is_dir())


def test_name():
    name = "test_object"
    with TemporaryDirectory() as parent_path:
        json_object = JSONObject(name, parent_path)
        assert(json_object.name == name)


def test_path():
    name = "test_object"
    with TemporaryDirectory() as parent_path:
        json_object = JSONObject(name, parent_path)
        object_path = Path(parent_path) / name
        assert(json_object.path == str(object_path))


def test_json_path():
    name = "test_object"
    with TemporaryDirectory() as parent_path:
        json_object = JSONObject(name, parent_path)
        json_path = Path(parent_path) / name / "{}.json".format(name)
        assert(json_object.json_path == str(json_path))


class JSONTestObject(JSONObject):

    def __init__(self, name, parent_path, value):
        super().__init__(name, parent_path)
        self["value"] = value


def test_save():
    name = "test_object"
    with TemporaryDirectory() as parent_path:
        json_object = JSONTestObject(name, parent_path, 3.14)
        json_object.save()
        json_path = Path(parent_path) / name / "{}.json".format(name)
        assert(json_path.exists())
        assert(json_path.is_file())
        with open(json_path, "r") as json_file:
            data = json.load(json_file)
            assert("value" in data)
            assert(data["value"] == 3.14)


def test_load():
    name = "test_object"
    with TemporaryDirectory() as parent_path:
        object_path = Path(parent_path) / name
        object_path.mkdir()
        json_path = Path(parent_path) / name / "{}.json".format(name)
        with open(json_path, "w") as json_file:
            json.dump({"value": 3.14}, json_file)
        json_object = JSONTestObject.load(json_path)
        assert(json_object.name == name)
        assert(json_object.path == str(object_path))
        assert(json_object["value"] == 3.14)
