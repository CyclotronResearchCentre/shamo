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
    :widths: 20 40 40
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

Gmsh
~~~~

`Gmsh <https://gmsh.info/>`_ is a 3D finite element mesher.
Download the latest version corresponding to your OS.

.. list-table:: Gmsh
    :widths: 20 80
    :header-rows: 1

    * - OS
      - Link
    * - Linux
      - `Gmsh Linux 32-bit <https://gmsh.info/bin/Linux/gmsh-4.7.1-Linux32-sdk.tgz>`_ or `Gmsh Linux 64-bit <https://gmsh.info/bin/Linux/gmsh-4.7.1-Linux64-sdk.tgz>`_
    * - Windows
      - `Gmsh Windows 32-bit <https://gmsh.info/bin/Windows/gmsh-4.7.1-Windows32-sdk.zip>`_ or `Gmsh Windows 64-bit <https://gmsh.info/bin/Windows/gmsh-4.7.1-Windows64-sdk.zip>`_
    * - MacOS
      - `Gmsh MacOS <https://gmsh.info/bin/MacOSX/gmsh-4.7.1-MacOSX-sdk.tgz>`_

Once downloaded, extract it and add it to the path.

GetDP
~~~~~

`GetDP <http://getdp.info/>`_ is a finite element solver which works in symbiosis with Gmsh.
Download the latest version corresponding to your OS.

.. list-table:: GetDP
    :widths: 20 80
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

Install shamo
-------------

Pip
~~~

Since ``shamo`` is available on `PyPI <https://pypi.org/project/shamo/>`_, the easiest way to install the latest release is to use the following command:

.. code-block:: shell

    python3 -m pip install shamo

Setup.py
~~~~~~~~

If you want to install from source, simply clone the repository and use the following command:

.. code-block:: shell

    python3 setup.py install --user
