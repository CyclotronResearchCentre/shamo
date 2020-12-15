API reference
=============

.. toctree::
   :maxdepth: 1

FEM
~~~

The :py:class:`FEM <shamo.core.fem.fem.FEM>` class contains all the classes and methods required to build a proper finite element model.

To construct the mesh, use one of the following methods:

* :py:func:`mesh_from_array <shamo.core.fem.fem.FEM.mesh_from_array>`
* :py:func:`mesh_from_nii <shamo.core.fem.fem.FEM.mesh_from_nii>`
* :py:func:`mesh_from_masks <shamo.core.fem.fem.FEM.mesh_from_masks>`
* :py:func:`mesh_from_niis <shamo.core.fem.fem.FEM.mesh_from_niis>`

Next, add fields to the mesh with:

* :py:func:`field_from_elems <shamo.core.fem.fem.FEM.field_from_elems>`
* :py:func:`field_from_array <shamo.core.fem.fem.FEM.field_from_array>`
* :py:func:`field_from_nii <shamo.core.fem.fem.FEM.field_from_nii>`

Finally, add sensors with:

* :py:func:`add_point_sensor <shamo.core.fem.fem.FEM.add_point_sensor>`
* :py:func:`add_point_sensor_on <shamo.core.fem.fem.FEM.add_point_sensor_on>`
* :py:func:`add_point_sensor_in <shamo.core.fem.fem.FEM.add_point_sensor_in>`
* :py:func:`add_point_sensors <shamo.core.fem.fem.FEM.add_point_sensors>`
* :py:func:`add_point_sensors_on <shamo.core.fem.fem.FEM.add_point_sensors_on>`
* :py:func:`add_point_sensors_in <shamo.core.fem.fem.FEM.add_point_sensors_in>`
* :py:func:`add_point_sensors_from_tsv <shamo.core.fem.fem.FEM.add_point_sensors_from_tsv>`
* :py:func:`add_point_sensors_from_tsv_on <shamo.core.fem.fem.FEM.add_point_sensors_from_tsv_on>`
* :py:func:`add_point_sensors_from_tsv_in <shamo.core.fem.fem.FEM.add_point_sensors_from_tsv_in>`
