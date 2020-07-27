# shamo

[![Code style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)


Constructing accurate subject specific head model is of main interest in the fields of source imaging (EEG/MEG) and brain stimulation (tDCS/tMS). shamo is an open source python package to calculate EEG leadfields, current flows, and electric potential distribution in the head. From a labelled 3D image of the head, the whole process is fully automatized, relying only on a few parameter files, e.g. conductivities (including white matter anisotropy) plus source and electrode locations. Since there is no non-invasive method to measure the electromagnetic (EM) properties of the head tissues, shamo can also be used to assess the sensitivity of the EM head model to these parameters.

For more information, see [the documentation](https://cyclotronresearchcentre.github.io/shamo/index.html).
