Finite element model creation
=============================

Creating a proper finite element model of the subject's head is the first step to solve forward problems or run simulations.
In :mod:`shamo`, it only takes a few lines of code. 
In the following example, we will generate a :class:`FEModel <shamo.model.fe_model.FEModel>` for a simple labeled volume but the steps are the same as for a more complex one.

Model initialization
--------------------

First, we have to create a new instance of the :class:`FEModel <shamo.model.fe_model.FEModel>` class:

.. code-block:: python
    :linenos:
    
    from shamo import FEModel
    
    model = FEModel("example_model", ".")

Here we have defined a model called ``"example_model"`` located in the current directory. 
A folder with this name should have appeared.

Mesh generation
---------------

Now that we have a :class:`FEModel <shamo.model.fe_model.FEModel>` instance, we have to generate the mesh.
To do so, we need a labeled volume.
In :mod:`shamo`, you can achieve this using multiple methods:

- :func:`mesh_from_labels <shamo.model.fe_model.FEModel.mesh_from_labels>`: Use this if you have a :class:`numpy.ndarray` containing ``uint8`` labels from ``0`` (air) to ``n`` (the n-th tissue).
- :func:`mesh_from_nii <shamo.model.fe_model.FEModel.mesh_from_nii>`: Use this if you have stored the exact same data as above in a ``.nii`` image.
- :func:`mesh_from_masks <shamo.model.fe_model.FEModel.mesh_from_masks>`: Use this if you have stored each tissue class in separate :class:`numpy.ndarray`.
- :func:`mesh_from_niis <shamo.model.fe_model.FEModel.mesh_from_niis>`: Use this if you have stored each tissue class in separate ``.nii`` images.

In this example, we will generate a single :class:`numpy.ndarray` containing all the labels and thus we will be using :func:`mesh_from_labels <shamo.model.fe_model.FEModel.mesh_from_labels>`.
For more information on the methods, refer to the corresponding documentation.

.. code-block:: python
    :linenos:
    
    import numpy as np
    
    # Generate the labels
    labels = np.ones((11, 11, 11), dtype=np.uint8)
    labels[3:-3, 3:-3, 3:-3] = 2
    labels[2:-5, 2:-5, 2:-5] = 3
    affine = np.diag([1, 1, 1, 1])
    tissues = ["a", "b", "c"]

The above generate ``labels`` is made of a big cube containing two smaller cubes. This is where you should place the code required to load your labels.
Next, we must define the parameters for the mesh generation. This is achieved by creating a :class:`MeshConfig <shamo.model.mesh_config.MeshConfig>` object and setting its attributes.

.. code-block:: python
    :linenos:
    
    from shamo import MeshConfig
    
    mesh_config = MeshConfig(facet_distance=1.5, cell_size=1)

.. note::
    The quality of the resulting mesh depends on these parameters. You should try to create the most accurate mesh you can before using it in next steps.

Now, we can pass all those variables to :func:`mesh_from_labels <shamo.model.fe_model.FEModel.mesh_from_labels>`.

.. code-block:: python
    :linenos:
    
    model.mesh_from_labels(labels, tissues, affine, mesh_config=mesh_config)

One run, this line generate a ``.msh`` file in the previously created directory. Those files can be opened using `Gmsh <http://gmsh.info/>`_.

Sensors placement
-----------------

We can now add sensors on the mesh using two methods:

- :func:`add_sensor <shamo.model.fe_model.FEModel.add_sensor>`: To add sensors one-by-one.
- :func:`add_sensors <shamo.model.fe_model.FEModel.add_sensors>`: To add multiple sensors at a time.

.. code-block:: python
    :linenos:
    
    coordinates = [(x, y, z) for x in (0, 10) for y in (0, 10) for z in (0, 10)]
    sensors = {chr(ord("A") + i): c for i, c in enumerate(coordinates)}

We have defined sensors manually for this example, but you should load their locations from experiment measurements.
Once the locations and the names of the sensors are defined, we can add them to the model on tissue ``"a"``.

.. code-block:: python
    :linenos:
    
    model.add_sensors(sensors, "a")

Anisotropy definition
---------------------

Anisotropic fields can be added to the model (e.g. white matter anisotropy). Once again, we can do this by using several methods:

- :func:`add_anisotropy_from_elements <shamo.model.fe_model.FEModel.add_anisotropy_from_elements>`: You might never use this as it requires the values of the field correspondign to each elements of the tissue you want to add anisotropy in.
- :func:`add_anisotropy_from_array <shamo.model.fe_model.FEModel.add_anisotropy_from_array>`: Use this if you have a :class:`numpy.ndarray` containing the field.
- :func:`add_anisotropy_from_nii <shamo.model.fe_model.FEModel.add_anisotropy_from_nii>`: Use this if you have a ``.nii`` image containing the field.

The fields can either be scalar fields or tensor fields. For the sake of this example, we generate a fake scalar field.

.. code-block:: python
    :linenos:
    
    field = np.ones((2, 2, 2)) * 0.1
    field[1, :, :] = 1
    field[:, 1, :] = 1
    field[:, :, 1] = 1
    affine = np.diag([10, 10, 10, 1])

We can now add it to the model.

.. code-block:: python
    :linenos:
    
    model.add_anisotropy_from_array(field, affine, "b", fill_value=1e-8, formula="<b>")

Model finalization
------------------

Our model is now complete. All we have to do is save it.

.. code-block:: python
    :linenos:
    
    model.save()

After this step, a ``.json`` file have been created in the model directory. 
This file contains all the information about the model and allow us to load it back in the future.

.. code-block:: python
    :linenos:
    
    model = FEModel.load("./example_model/example_model.json")
    
Full code
---------

.. code-block:: python
    :linenos:
    
    from shamo import FEModel, MeshConfig
    import numpy as np
    
    # Model initialization
    model = FEModel("example_model", ".")
    
    # Mesh generation
    labels = np.ones((11, 11, 11), dtype=np.uint8)
    labels[3:-3, 3:-3, 3:-3] = 2
    labels[2:-5, 2:-5, 2:-5] = 3
    affine = np.diag([1, 1, 1, 1])
    tissues = ["a", "b", "c"]
    
    mesh_config = MeshConfig(facet_distance=1.5, cell_size=1)
    model.mesh_from_labels(labels, tissues, affine, mesh_config=mesh_config)
    
    # Sensors placement
    coordinates = [(x, y, z) for x in (0, 10) for y in (0, 10) for z in (0, 10)]
    sensors = {chr(ord("A") + i): c for i, c in enumerate(coordinates)}
    
    model.add_sensors(sensors, "a")
    
    # Anisotropy definition
    field = np.ones((2, 2, 2)) * 0.1
    field[1, :, :] = 1
    field[:, 1, :] = 1
    field[:, :, 1] = 1
    affine = np.diag([10, 10, 10, 1])

    model.add_anisotropy_from_array(field, affine, "b", fill_value=1e-8, formula="<b>")

    # Finalization
    model.save()