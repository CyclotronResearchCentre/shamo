EEG forward problem resolution
==============================

Now that we have a proper :class:`FEModel <shamo.model.fe_model.FEModel>`, we can solve the EEG forward problem.

Model loading
-------------

First, we must load the finite element model.

.. code-block:: python
    :linenos:

    from shamo import FEModel
    
    model = FEModel.load("./example_model/example_model.json")

Problem initialization
----------------------

Now, we have to create a :class:`EEGForwardProblem <shamo.problems.forward.eeg.eeg_forward_problem.EEGForwardProblem>` instance.

.. code-block:: python
    :linenos:

    from shamo import EEGForwardProblem
    
    problem = EEGForwardProblem()

This object will hold all the settings for the problem and provide a solver.

Tissue conductivity definition
------------------------------

To solve the EEG forward problem, we must specify the electrical conductivity of the tissues [S/m].
We can use two methods for that:

- :func:`set_electrical_conductivity <shamo.problems.forward.forward_problem.ForwardProblem.set_electrical_conductivity>`: Use it to set the conductivity of tissues one-by-one.
- :func:`set_electrical_conductivities <shamo.problems.forward.forward_problem.ForwardProblem.set_electrical_conductivities>`: Use it to set the conductivity of multiple tissues at once.

.. code-block:: python
    :linenos:

    problem.set_electrical_conductivity("a", 1.0)
    sigmas = {"b": 0.5, "c": 0.25}
    problem.set_electrical_conductivities(sigmas, {"b": "b_anisotropy"})

We can also tell the solver to use previously added anisotropic fields by referencing them by their names.

Regions of interest definition
------------------------------

When computing a leadfield matrix, we must tell the solver which tissues we want the solution to be generated for.
Once again, two methods are available:

- :func:`add_region_of_interest <shamo.problems.forward.forward_problem.ForwardProblem.add_region_of_interest>`: Use it to add one tissue to the ROIs.
- :func:`add_regions_of_interest <shamo.problems.forward.forward_problem.ForwardProblem.add_regions_of_interest>`: Use it to add multiple tissues to he ROIs.

.. code-block:: python
    :linenos:
    
    problem.add_regions_of_interest(["b", "c"])

Here we ask the solver to compute the leadfield matrix for the combined volume made of the tissues ``"b"`` and ``"c"``.

Reference sensor definition
---------------------------

Next, we can define the sensor which will be used as a reference. This is achieved using :func:`set_reference <shamo.problems.forward.eeg.eeg_forward_problem.EEGForwardProblem.set_reference>`.

.. code-block:: python
    :linenos:
    
    problem.set_reference("A")

Markers definition
------------------

When using EEG, some sensors are only there for positioning purpose and do not play a role in the resolution of the problem.
In :mod:`shamo`, those are called markers and are simply ignored by the solver.
As always, we can use two methods to specify the markers:

- :func:`add_marker <shamo.problems.forward.forward_problem.ForwardProblem.add_marker>`: Use it to add one marker at a time.
- :func:`add_markers <shamo.problems.forward.forward_problem.ForwardProblem.add_markers>`: Use it to add multiple markers in a single call.

.. code-block:: python
    :linenos:
    
    problem.add_markers(["C", "G"])

Problem resolution
------------------

The problem is now fully defined and all we have to do is solve it using the :func:`solve <shamo.problems.forward.eeg.eeg_forward_problem.EEGForwardProblem.solve>` method.

.. code-block:: python
    :linenos:
    
    solution = problem.solve("example_leadfield", ".", model)

This step will produce an :class:`EEGForwardSolution <shamo.solutions.eeg.eeg_forward_solution.EEGForwardSolution>` instance which contains the leadfield matrix and all the problem settings.

Full code
---------

.. code-block:: python
    :linenos:
    
    from shamo import FEModel, EEGForwardProblem
    
    # Model loading
    model = FEModel.load("./example_model/example_model.json")
    
    # Problem initialization
    problem = EEGForwardProblem()
    
    # Tissue conductivity definition
    problem.set_electrical_conductivity("a", 1.0)
    sigmas = {"b": 0.5, "c": 0.25}
    problem.set_electrical_conductivities(sigmas, {"b": "b_anisotropy"})
    
    # Regions of interest definition
    problem.add_regions_of_interest(["b", "c"])
    
    # Reference sensor definition
    problem.set_reference("A")
    
    # Markers definition
    problem.add_markers(["C", "G"])
    
    # Problem resolution
    solution = problem.solve("example_leadfield", ".", model)