Install
=======

.. toctree::
   :maxdepth: 1


.. warning::
    Only tested on Ubuntu 18.10+.

Install binary dependencies
---------------------------

CGAL
~~~~

`CGAL <https://www.cgal.org/index.html>`_ is a geometry package which provides fast and reliable algorithms written in C++.
We recommend you to use the package manager of your OS.

.. list-table:: CGAL
    :widths: 25 50 50
    :header-rows: 1
    
    * - OS
      - Package manager
      - Link
    * - Linux
      - ``sudo apt-get install libcgal-dev``
      - `CGAL for Linux <https://www.cgal.org/download/linux.html>`_
    * - Windows
      - ``vcpkg install cgal``
      - `CGAL for Windows <https://www.cgal.org/download/windows.html>`_
    * - MacOS
      - ``brew install cgal``
      - `CGAL for MacOS <https://www.cgal.org/download/macosx.html>`_

GetDP
~~~~~

`GetDP <http://getdp.info/>`_ is a finite element solver which works in symbiosis with Gmsh.
Download the latest version corresponding to your OS.

.. list-table:: GetDP
    :widths: 25 100
    :header-rows: 1
    
    * - OS
      - Link
    * - Linux
      - `GetDP Linux 32-bit <http://getdp.info/bin/Linux/getdp-3.3.0-Linux32c.tgz>`_ or `GetDP Linux 64-bit <http://getdp.info/bin/Linux/getdp-3.3.0-Linux64c.tgz>`_
    * - Windows
      - `GetDP Windows 32-bit <http://getdp.info/bin/Windows/getdp-3.3.0-Windows32c.zip>`_ or `GetDP Windows 64-bit <http://getdp.info/bin/Windows/getdp-3.3.0-Windows64c.zip>`_
    * - MacOS
      - `GetDP MacOS <http://getdp.info/bin/MacOSX/getdp-3.3.0-MacOSXc.tgz>`_

Once downloaded, extract it and add it to the path.

Install python dependencies
---------------------------

Using ``pip``, install the following packages:

.. list-table:: Python packages
    :widths: 25 50 50
    :header-rows: 1
    
    * - Package
      - Version
      - Link
    * - Numpy
      - >=1.16.2
      - `numpy.org <https://numpy.org/>`_
    * - Scipy
      - >=1.4.0
      - `scipy.org <https://www.scipy.org/>`_
    * - Nibabel
      - >=2.5.0
      - `nipy.org <https://nipy.org/nibabel/>`_
    * - Pygalmesh
      - ==0.4.0
      - `pygalmesh <https://github.com/nschloe/pygalmesh>`_
    * - Gmsh
      - >=4.5.6
      - `gmsh.info <http://gmsh.info/>`_
    * - Chaospy
      - >=3.2.8
      - `chaospy.readthedocs.io <https://chaospy.readthedocs.io/en/master/>`_

You simply have to issue the following command in a terminal:

.. code-block:: shell
    
    python3 -m pip install --user numpy scipy nibabel pygalmesh==0.4.0 gmsh chaospy

Install shamo
-------------

For now, ``shamo`` is still not available using ``pip`` so clone or download the latest release from `github <https://github.com/CyclotronResearchCentre/shamo>`_
and issue the following command:

.. code-block:: shell
    
    python3 setup.py install --user