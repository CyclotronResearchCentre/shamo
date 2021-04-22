Logging
=======

This package uses the standard :py:mod:`logging` module. To use it, we simply have to acquire the logger.

.. code-block:: python

   import shamo
   import logging

   logger = logging.getLogger("shamo")

Then we can configure it anyway we want. To display the output in a jupyter notebook, we can for instance use:

.. code-block:: python

   import sys

   stream_handler = logging.StreamHandler(sys.stdout)
   stream_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
   logger.addHandler(stream_handler)
   logger.setLevel(logging.INFO)

.. note::

   This package heavily relies on C++ programs and tries as much as possible to redirect their output through the logging module.
   Still, some libraries keep printing to different streams and might not show properly depending on the environment you run *shamo* in such as IPython.
