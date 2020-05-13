API reference
=============

The public API of :mod:`shamo` only provides a subset of the classes and methods defined in the package.
Here is a quick description of the exposed classes.

Finite element model
--------------------

- :class:`FEModel <shamo.model.fe_model.FEModel>`: The model itself which holds all the data and provides all the methods.
- :class:`MeshConfig <shamo.model.mesh_config.MeshConfig>`: The parameters passed to the meshing algorithm.

Problems
--------

EEG
~~~
- :class:`EEGForwardProblem <shamo.problems.forward.eeg.eeg_forward_problem.EEGForwardProblem>`: A problem used to generate a single leadfield matrix.
- :class:`EEGParametricForwardProblem <shamo.problems.forward.eeg.eeg_parametric_forward_problem.EEGParametricForwardProblem>`: A problem used to generate a parametric leadfield matrix.
- :class:`EEGSimulationProblem <shamo.problems.forward.eeg.eeg_simulation_problem.EEGSimulationProblem>`: A problem to simulate sources in the brain for EEG.

Solutions
---------

EEG
~~~
- :class:`EEGForwardSolution <shamo.solutions.forward.eeg.eeg_forward_solution.EEGForwardSolution>`: A single leadfield matrix.
- :class:`EEGParametricForwardSolution <shamo.solutions.forward.eeg.eeg_parametric_forward_solution.EEGParametricForwardSolution>`: A parametric leadfield matrix.
- :class:`EEGSimulationSolution <shamo.solutions.forward.eeg.eeg_simulation_solution.EEGSimulationSolution>`: A simulation of sources in the brain for EEG.


Sources
-------

- :class:`FESource <shamo.model.sources.fe_source.FESource>`: A source defined in a finite element model.
- :class:`EEGSource <shamo.model.sources.eeg_source.EEGSource>`: A source defined in an EEG problem.

Distributions
-------------

- :class:`ConstantDistribution <shamo.core.distribution.ConstantDistribution>`: For a property with a fixed value.
- :class:`UniformDistribution <shamo.core.distribution.UniformDistribution>`: For a property with uniformly distributed values.