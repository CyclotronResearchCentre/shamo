Welcome to shamo's documentation!
=================================

.. toctree::
   :maxdepth: 1

   quickstart/quickstart
   api/api
   reference/reference


Introduction
------------

Constructing accurate subject specific head model is of main interest in the fields of source imaging (EEG/MEG) and brain stimulation (tDCS/tMS).
*shamo* is an open source python package to calculate EEG leadfields, current flows, and electric potential distribution in the head.
From a labelled 3D image of the head, the whole process is fully automatized, relying only on a few parameter files, e.g. conductivities (including white matter anisotropy) plus source and electrode locations.
Since there is no non-invasive method to measure the electromagnetic (EM) properties of the head tissues, *shamo* can also be used to assess the sensitivity of the EM head model to these parameters.

Philosophy
----------

The idea leading the development of *shamo* is to provide a versatile, intuitive and extendable toolbox for electromagnetic modelling of the head.
Every object is though to be savable/loadable as a dictionary and stored as a JSON file on disk.
*shamo* is built around three main concepts:

#. **Problem:** The definition of a task to perform. Computing the EEG leadfield or simulating tDCS for examples.
#. **Solution:** The object resulting from the resolution of a problem.
#. **Surrogate:** If the problem-solution pair is parametric, e.g. some parameters are random variables, surrogate can be used to produce parametric models.

One of the leading rules while working on *shamo* was to use already existing quality tools to perform key steps.
Thus, the finite element generation is achieved by interfacing with `CGAL <https://www.cgal.org/>`_ and `Gmsh <https://gmsh.info/>`_, the physical problem resolution is done with `GetDP <https://getdp.info/>`_, the Gaussian processes are generated with `scikit-learn <https://scikit-learn.org/stable/>`_ and the sensitivity analysis uses `SALib <https://salib.readthedocs.io/en/latest/>`_.
