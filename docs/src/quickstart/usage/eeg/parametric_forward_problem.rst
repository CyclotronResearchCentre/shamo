EEG parametric forward problem resolution
=========================================

On of the goals of :mod:`shamo` is to provide a way to create parametric solutions for the forward problem.
For EEG, this is achieved using :class:`EEGParametricForwardProblem <shamo.problems.forward.eeg.eeg_parametric_forward_problem.EEGParametricForwardProblem>`.

Model loading
-------------

First, we must load the finite element model.

.. code-block:: python
    :linenos:

    from shamo import FEModel

    model = FEModel.load("./example_model/example_model.json")

Problem definition
------------------

As for the normal :class:`EEGForwardProblem <shamo.problems.forward.eeg.eeg_forward_problem.EEGForwardProblem>`, we have to define several parameters.
The code is almost the same.

.. code-block:: python
    :emphasize-lines: 1,7,8,9,10,11
    :linenos:

    from shamo import EEGParametricForwardProblem, ConstantDistribution, UniformDistribution

    # Problem initialization
    problem = EEGParametricForwardProblem()

    # Tissues conductivity definition
    problem.set_electrical_conductivities({
        "a": ConstantDistribution(1.0),
        "c": UniformDistribution(0.25, 0.75)
    })
    problem.set_electrical_conductivity("b", UniformDistribution(0.1, 0.9), "b_anisotropy")

    # Set definition
    problem.set_reference("A")

    # Markers definition
    problem.add_markers(["C", "G"])

    # Regions of interest definition
    problem.add_regions_of_interest(["b", "c"])

Here, the only difference is that we pass the electrical conductivity of the tissues as :class:`Distribution <shamo.core.distribution.Distribution>` objects.
As you can see, tissues with fixed conductivity values are given a :class:`ConstantDistribution <shamo.core.distribution.ConstantDistribution>`

Problem resolution
------------------

As for all the problems in :mod:`shamo`, the solver is called with :func:`solve <shamo.problems.forward.eeg.eeg_parametric_forward_problem.EEGParametricForwardProblem.solve>`.
For parametric problems which require several computations of smaller problems, we can choose the way we want to make the jobs parallel using the ``method`` parameter:

- ``METHOD_SEQ``: Use it to run all the processes sequentially.
- ``METHOD_MULTI``: Use it to use the :mod:`multiprocessing` module.
- ``METHOD_MPI``: Use it to use the :mod:`mpi4py` module.
- ``METHOD_JOBS``: Use it to generate separate python scripts corresponding to each job. Those scripts can run on a cluster or on multiple machines. If you use this method, run :func:`finalize <shamo.solutions.forward.eeg.eeg_parametric_forward_solution.EEGParametricForwardSolution.finalize>` once you have gathered all the solutions.

.. warning::

    The ``METHOD_MPI`` method is not yet implemented.

.. code-block:: python
    :linenos:

    solution = problem.solve("parametric_leadfield", ".", model,
                             method=EEGParametricForwardProblem.METHOD_MULTI)

We now have a proper parametric leadfield modeled by a Gaussian process.

Full code
---------

.. code-block:: python
    :linenos:

    from shamo import (FEModel, EEGParametricForwardProblem,
                       ConstantDistribution, UniformDistribution)

    # Model loading
    model = FEModel.load("./example_model/example_model.json")

    # Problem initialization
    problem = EEGParametricForwardProblem()

    # Tissues conductivity definition
    problem.set_electrical_conductivities({
        "a": ConstantDistribution(1.0),
        "c": UniformDistribution(0.25, 0.75)
    })
    problem.set_electrical_conductivity("b", UniformDistribution(0.1, 0.9), "b_anisotropy")

    # Set definition
    problem.set_reference("A")

    # Markers definition
    problem.add_markers(["C", "G"])

    # Regions of interest definition
    problem.add_regions_of_interest(["b", "c"])

    # Problem resolution
    solution = problem.solve("parametric_leadfield", ".", model,
                             method=EEGParametricForwardProblem.METHOD_MULTI)
