# shamo

[![version](https://img.shields.io/pypi/v/shamo?color=black&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/shamo/)
![python](https://img.shields.io/pypi/pyversions/shamo?logo=python&logoColor=white&color=black&style=flat-square)
[![documentation](https://img.shields.io/badge/docs-github_pages-black?style=flat-square&logo=read-the-docs&logoColor=white)](https://cyclotronresearchcentre.github.io/shamo/index.html)
[![tutorials](https://img.shields.io/badge/tutorials-jupyter_notebooks-black?style=flat-square&logo=jupyter&logoColor=white)](https://cyclotronresearchcentre.github.io/shamo/index.html)
[![codestyle](https://img.shields.io/badge/codestyle-black-black?style=flat-square)](https://github.com/psf/black)
[![docstyle](https://img.shields.io/badge/docstyle-numpydoc-black?style=flat-square)](https://numpydoc.readthedocs.io/en/latest/)
[![license](https://img.shields.io/pypi/l/shamo?color=black&style=flat-square&logo=gnu&logoColor=white)](https://github.com/CyclotronResearchCentre/shamo/blob/master/LICENSE.md)  
[![doi](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.4420811-black?style=flat-square)](https://doi.org/10.5281/zenodo.4420811)

## Introduction

Constructing accurate subject specific head model is of main interest in the fields of source imaging (EEG/MEG) and brain stimulation (tDCS/tMS). *shamo* is an open source python package to calculate EEG leadfields, current flows, and electric potential distribution in the head. From a labelled 3D image of the head, the whole process is fully automatized, relying only on a few parameter files, e.g. conductivities (including white matter anisotropy) plus source and electrode locations. Since there is no non-invasive method to measure the electromagnetic (EM) properties of the head tissues, *shamo* can also be used to assess the sensitivity of the EM head model to these parameters.

## Philosophy

The idea leading the development of *shamo* is to provide a versatile, intuitive and extendable toolbox for electromagnetic modelling of the head.
Every object is though to be savable/loadable as a dictionary and stored as a JSON file on disk.
*shamo* is built around three main concepts:

1. **Problem:** The definition of a task to perform. Computing the EEG leadfield or simulating tDCS for examples.
1. **Solution:** The object resulting from the resolution of a problem.
1. **Surrogate:** If the problem-solution pair is parametric, e.g. some parameters are random variables, surrogate can be used to produce parametric models.

One of the leading rules while working on *shamo* was to use already existing quality tools to perform key steps.
Thus, the finite element generation is achieved by interfacing with [CGAL](https://www.cgal.org/) and [Gmsh](https://gmsh.info/), the physical problem resolution is done with [GetDP](https://getdp.info/), the Gaussian processes are generated with [scikit-learn](https://scikit-learn.org/stable/) and the sensitivity analysis uses [SALib](https://salib.readthedocs.io/en/latest/).

## Documentation

The documentation of *shamo* is available [here](https://cyclotronresearchcentre.github.io/shamo/index.html) and tutorials are available in the form of jupyter notebooks in [this repository](https://github.com/CyclotronResearchCentre/shamo-tutorials).

## FAQ

### Where can you get help about *shamo*?

If you need help with your project involving *shamo*, head over to [this page](https://github.com/CyclotronResearchCentre/shamo/issues/new) and pick up the help template. Make sure your question does not already exist fy searching the issues.

We'll be happy to give you some help!

### Where does the name *"shamo"* come from?
The name *"shamo"*, pronounced [ʃɑ:mɔ:], stands for *"Stochastic HeAd MOdelling"*.

In french, it sounds like the word *"chameau"* which is the translation for *"camel"*. This is a reference to the bematists, those ancient greek and egyptians who were able to measure distances with a high accuracy by counting the steps of a camel. They were involved in the accurate calculation of the circumference of the Earth by limiting distance measurement errors.

As did the old bematists, this tool aims at raising the accuracy in outcome of neuro- studies by providing more insights on the errors involved.

### How to contribute?

You can contribute to *shamo* in several ways like adding new features, fixing bugs or improving documentation and examples.

For more information, refer to [this document](CONTRIBUTING.md).

## License

Copyright (C) 2020 [GIGA CRC In-Vivo Imaging](https://www.giga.uliege.be/cms/c_5634375/fr/giga-in-vivo-imaging), Liège, Belgium

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

For more information, refer to [the full license](LICENSE.md).
