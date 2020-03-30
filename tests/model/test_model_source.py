from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

import numpy as np
import gmsh

from shamo import FEModel, EEGSource

MODEL_PATH = str(Path("tests/data/model_1"))


def _check_model_sources(model, sources):
    assert(len(model.sources) == len(sources))
    for source in sources:
        assert(model.source_exists(source))
    # Check if mesh is properly created
    gmsh.initialize()
    gmsh.open(model.mesh_path)
    tags = gmsh.model.mesh.getElements(
        3, model.tissues["b"].volume_entity[0])[1]
    tags = np.array(tags).flatten()
    assert(tags.size > 0)
    gmsh.finalize()


def test_add_sources():
    with TemporaryDirectory() as parent_path:
        # Load model
        shutil.copytree(MODEL_PATH, str(Path(parent_path) / "model_1"))
        model_path = str(Path(parent_path) / "model_1/model_1.json")
        model = FEModel.load(model_path)
        # Add source
        sources = [EEGSource((6.25, 6.25, 6.25), (1, 0, 0), 1)]
        model.add_sources(sources, "b")
        model.save()
        # Test the model
        _check_model_sources(model, sources)
