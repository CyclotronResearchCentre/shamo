EEG simulation
==============

To validate a leadfield matrix, it is interesting to be able to directly simulate sources in the brain.
In :mod:`shamo`, this is performed using :class:`EEGSimulationProblem <shamo.problems.forward.eeg.eeg_simulation_problem.EEGSimulationProblem>`.

Sources definition
------------------

Before creating the finite element model, we should define a list of sources we want to simulate.
For EEG, these sources are instances of the :class:`EEGSource <shamo.model.sources.eeg_source.EEGSource>` class.
Each source is characterized by its coordinates in space [mm], its pointing vector and its current dipole moment [Am].

.. code-block:: python
    :linenos:
    
    from shamo import EEGSource

    sources = [EEGSource((6, 6, 6), (1, 0, 0), 1e-6)]

For this example, we only define one source but you can add as many as you need.

Model creation
--------------

We first have to create the :class:`FEModel <shamo.model.fe_model.FEModel>` instance. 
This step is almost the same as for solving the forward problem so here is the code.

.. code-block:: python
    :emphasize-lines: 18
    :linenos:
    
    import numpy as np
    from shamo import FEModel, MeshConfig

    # Model initialization
    model = FEModel("sim_model", ".")
    
    # Mesh generation
    labels = np.ones((11, 11, 11), dtype=np.uint8)
    labels[3:-3, 3:-3, 3:-3] = 2
    labels[2:-5, 2:-5, 2:-5] = 3
    tissues = ["a", "b", "c"]
    affine = np.diag([1, 1, 1, 1])
    mesh_config = MeshConfig(facet_distance=1.5, cell_size=1)
    model.mesh_from_labels(labels, tissues, affine, 
                               mesh_config=mesh_config)

    # Sources placement
    model.add_sources(sources, "b", lc=1e-4)

    # Sensors placement
    coordinates = [(x, y, z) for x in (0, 10) for y in (0, 10) 
                   for z in (0, 10)]
    sensors = {chr(ord("A") + i): c for i, c in enumerate(coordinates)}
    model.add_sensors(sensors, "a")

    # Anisotropy definition
    field = np.ones((2, 2, 2)) * 0.1
    field[1, :, :] = 1
    field[:, 1, :] = 1
    field[:, :, 1] = 1
    affine = np.diag([10, 10, 10, 1])
    model.add_anisotropy_from_array(field, affine, "b",
                                    fill_value=1e-8, formula="<b>")

    # Finalization
    model.save()

As you can see, the only added line is used to add the sources to the mesh through :func:`add_sources <shamo.model.fe_model.FEModel.add_sources>`. 

.. warning::
    
    Adding sources is a destructive step. 
    You must always add sources before adding other information to the mesh.

.. note::
        
    Simulating sources requires to create a finite element model containing the sources. 
    As building such model can be time consuming, we recommend you to build a model containing all the sources you want to simulate.
    You can then choose which one to use during the simulation so that you run multiple tests based on a single model.

Problem definition
------------------

As always in :mod:`shamo`, we must define a problem we want to solve. 
The :class:`EEGSimulationProblem <shamo.problems.forward.eeg.eeg_simulation_problem.EEGSimulationProblem>` is very similar to the :class:`EEGForwardProblem <shamo.problems.forward.eeg.eeg_forward_problem.EEGForwardProblem>`.
We still have to define the electrical conductivity of the tissues, the reference sensor and the markers.

.. code-block:: python
    :linenos:
    
    from shamo import EEGSimulationProblem

    # Problem initialization
    problem = EEGSimulationProblem()

    # Tissue conductivity definition
    sigmas = {"a": 1.0, "b": 0.5, "c": 0.25}
    problem.set_electrical_conductivities(sigmas, {"b": "b_anisotropy"})

    # Reference sensor definition
    problem.set_reference("A")

    # Markers definition
    problem.add_markers(["C", "G"])

Now, we just have to specify the sources we want to simulate using one of these methods:

- :func:`add_source <shamo.problems.forward.eeg.eeg_simulation_problem.EEGSimulationProblem.add_source>`: Use it to add one source.
- :func:`add_sources <shamo.problems.forward.eeg.eeg_simulation_problem.EEGSimulationProblem.add_sources>`: Use it to add multiple sources.

.. code-block:: python
    :linenos:
    
    problem.add_sources(sources)

Problem resolution
------------------

All we have left to do is to solve the problem.

.. code-block:: python
    :linenos:
    
    simulation = problem.solve("simulation", ".", model)

Solving this problem will create a directory containing results which can be viewed using Gmsh but also provide the potential measured by the sensors.

Full code
---------

.. code-block:: python
    :linenos:
    
    import numpy as np
    from shamo import EEGSource, FEModel, MeshConfig, EEGSimulationProblem

    # Sources definition
    sources = [EEGSource((6, 6, 6), (1, 0, 0), 1e-6)]

    # Model initialization
    model = FEModel("sim_model", ".")
    
    # Mesh generation
    labels = np.ones((11, 11, 11), dtype=np.uint8)
    labels[3:-3, 3:-3, 3:-3] = 2
    labels[2:-5, 2:-5, 2:-5] = 3
    tissues = ["a", "b", "c"]
    affine = np.diag([1, 1, 1, 1])
    mesh_config = MeshConfig(facet_distance=1.5, cell_size=1)
    model.mesh_from_labels(labels, tissues, affine, 
                               mesh_config=mesh_config)

    # Sources placement
    model.add_sources(sources, "b", lc=1e-4)

    # Sensors placement
    coordinates = [(x, y, z) for x in (0, 10) for y in (0, 10) 
                   for z in (0, 10)]
    sensors = {chr(ord("A") + i): c for i, c in enumerate(coordinates)}
    model.add_sensors(sensors, "a")

    # Anisotropy definition
    field = np.ones((2, 2, 2)) * 0.1
    field[1, :, :] = 1
    field[:, 1, :] = 1
    field[:, :, 1] = 1
    affine = np.diag([10, 10, 10, 1])
    model.add_anisotropy_from_array(field, affine, "b",
                                    fill_value=1e-8, formula="<b>")

    # Finalization
    model.save()
    
    # Problem initialization
    problem = EEGSimulationProblem()

    # Tissue conductivity definition
    sigmas = {"a": 1.0, "b": 0.5, "c": 0.25}
    problem.set_electrical_conductivities(sigmas, {"b": "b_anisotropy"})

    # Reference sensor definition
    problem.set_reference("A")

    # Markers definition
    problem.add_markers(["C", "G"])
    
    # Source selection
    problem.add_sources(sources)
    
    # Problem resolution
    simulation = problem.solve("simulation", ".", model)