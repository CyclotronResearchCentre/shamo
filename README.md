# shamo

[![PyPI version](https://img.shields.io/pypi/v/shamo?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/shamo/) ![Python](https://img.shields.io/pypi/pyversions/shamo?logo=python&logoColor=white) [![License](https://img.shields.io/pypi/l/shamo?color=blue)](https://github.com/CyclotronResearchCentre/shamo/blob/master/LICENSE.md)  
[![Docker](https://img.shields.io/badge/docker-python%20%7C%20jupyter%20lab-blue?logo=docker&logoColor=white)](https://hub.docker.com/repository/docker/margrignard/shamo/general) [![Documentation](https://img.shields.io/badge/docs-read%20the%20docs-blue?logo=read%20the%20docs&logoColor=white)](https://cyclotronresearchcentre.github.io/shamo/index.html) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/CyclotronResearchCentre/shamo-tutorials/master)  
[![Code style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black) [![Doc style](https://img.shields.io/badge/doc%20style-numpydoc-blue)](https://numpydoc.readthedocs.io/en/latest/)


Constructing accurate subject specific head model is of main interest in the fields of source imaging (EEG/MEG) and brain stimulation (tDCS/tMS). shamo is an open source python package to calculate EEG leadfields, current flows, and electric potential distribution in the head. From a labelled 3D image of the head, the whole process is fully automatized, relying only on a few parameter files, e.g. conductivities (including white matter anisotropy) plus source and electrode locations. Since there is no non-invasive method to measure the electromagnetic (EM) properties of the head tissues, shamo can also be used to assess the sensitivity of the EM head model to these parameters.

## Install

Before installing `shamo`, make sure to [install the dependencies](https://cyclotronresearchcentre.github.io/shamo/quickstart/install.html).

Once done, you can either install it from [PyPI](https://pypi.org/project/shamo/):
```shell
python3 -m pip install shamo
```

or from source:
```shell
git clone https://github.com/CyclotronResearchCentre/shamo
cd shamo
python3 setup.py install
```

`shamo` is also available on [docker hub](https://hub.docker.com/repository/docker/margrignard/shamo/general) in four different images:
- `python-dev` and `jupyter-dev` provide the latest build from the `develop` branch.
- `python-{tag}` and `jupyter-{tag}` provide builds for corresponding releases.
The `python` images provide a python interpreter with shamo installed where the`jupyter` images also provide a jupyter lab server.

For more information, see [the documentation](https://cyclotronresearchcentre.github.io/shamo/index.html).
