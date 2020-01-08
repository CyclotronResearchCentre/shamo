import nibabel as nib
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import gmsh

from .anisotropy import Anisotropy


def add_anisotropy_from_elements(self, element_tags, element_values,
                                 in_tissue, fill_value, formula="1"):
    """Add an anisotropic field to the model.

    Add an anisotropic field to the model based on elements values.

    Parameters
    ----------
    element_tags : np.ndarray
        The tags of the elements to add anisotropy in.
    element_values : np.ndarray
        The corresponding values.
    in_tissue : str
        The name of the tissue to add anisotropy in.
    fill_value : float
        The value used in elements not included in `element_tags` but still in
        the same tissue.
    formula : str, optional
        The formula to compute the coefficient with. (The default is `1`).

    Returns
    -------
    FEModel
        The current model.

    Raises
    ------
    KeyError
        If the tissue defined by `in_tissue` is not included in the model.
    ValueError
        If `element_values` contains neither a scalar field nor a vector field
        nor a tensor field.
        If `fill_value` is not of the same size as the `element_values` values.

    See Also
    --------
    Anisotropy.evaluate_formula
    """
    # Check arguments
    if in_tissue not in self.tissues:
        raise KeyError(("Model does not contain tissue "
                        "'{}'.").format(in_tissue))
    if element_values.size == element_tags.size:
        n_values = 1
        anisotropy_type = Anisotropy.SCALAR
    elif element_values.size == 3 * element_tags.size:
        n_values = 3
        anisotropy_type = Anisotropy.VECTOR
    elif element_values.size == 9 * element_tags.size:
        n_values = 9
        anisotropy_type = Anisotropy.TENSOR
    else:
        raise ValueError(("Values in `element_values` must be scalars, "
                          "3D vectors or 3D tensors."))
    if np.array(fill_value).size != n_values:
        print(n_values, np.array(fill_value).size)
        raise ValueError(("The `fill_value` must be of the same size as the "
                          "field values."))
    element_values = element_values.flatten()
    gmsh.initialize()
    gmsh.open(self.mesh_path)
    # Fill empty elements with `fill_value`
    all_element_tags = np.hstack([gmsh.model.mesh.getElements(3, entity)[1]
                                  for entity
                                  in self.tissues[in_tissue].volume_entity])
    empty_element_indices = np.isin(all_element_tags, element_tags,
                                    assume_unique=True, invert=True)
    empty_element_tags = all_element_tags[empty_element_indices]
    if empty_element_tags.size != 0:
        empty_element_values = np.broadcast_to(np.array(fill_value),
                                               (1, empty_element_tags.size
                                                * n_values))
        element_tags = np.hstack((element_tags, empty_element_tags))
        element_values = np.hstack((element_values,
                                    empty_element_values.flatten()))
    # Add anisotropy
    model = gmsh.model.list()[0]
    view = gmsh.view.add("{}_anisotropy".format(in_tissue))
    gmsh.view.addModelData(view, 0, model, "ElementData", element_tags,
                           element_values.reshape((-1, n_values)),
                           numComponents=n_values)
    gmsh.view.write(view, self.mesh_path, True)
    gmsh.finalize()
    if self.anisotropy is None:
        self["anisotropy"] = {}
    self["anisotropy"][in_tissue] = Anisotropy(anisotropy_type, view,
                                               formula)
    return self


def add_anisotropy_from_array(self, field, affine, in_tissue,
                              fill_value, formula="1",
                              nearest=False):
    """Add an anisotropic field to the model.

    Add an anisotropic field to the model based on a regular grid field.

    Parameters
    ----------
    field : np.ndarray
        The field array.
    affine : np.ndarray
        The affine matrix of the field.
    in_tissue : str
        The name of the tissue to add anisotropy in.
    fill_value : float
        The value used in elements not included in `element_tags` but still in
        the same tissue.
    formula : str, optional
        The formula to compute the coefficient with. (The default is `1`).
    nearest : bool, optional
        If set to `True`, no linear interpolation is performed and the nearest
        value is used. (The default is `False`).

    Returns
    -------
    FEModel
        The current model.

    Raises
    ------
    KeyError
        If the tissue defined by `in_tissue` is not included in the model.
    ValueError
        If `field` contains neither a scalar field nor a vector field nor a
        tensor field or if the values are not in the last dimension.

    See Also
    --------
    add_anisotropy_from_elements
    Anisotropy.evaluate_formula
    """
    # Check arguments
    if field.ndim != 3 and field.ndim != 4:
        raise ValueError("The argument `field` must be a 3D or 4D array.")
    if field.ndim == 4:
        if field.shape[-1] != 3 and field.shape[-1] != 9:
            raise ValueError(("Values in `element_values` must be scalars, "
                              "3D vectors or 3D tensors."))
    if affine.shape != (4, 4):
        raise ValueError("The argument `affine` must be a 4x4 array.")
    if in_tissue not in self.tissues:
        raise KeyError(("Model does not contain tissue "
                        "'{}'.").format(in_tissue))
    # Get cells coordinates
    field_flat_indices = np.arange(np.prod(field.shape[:3]))
    field_indices = \
        np.vstack(np.unravel_index(field_flat_indices, field.shape[:3])).T
    field_real_coordinates = nib.affines.apply_affine(affine, field_indices)
    # Create interpolator
    x = np.unique(field_real_coordinates[:, 0])
    y = np.unique(field_real_coordinates[:, 1])
    z = np.unique(field_real_coordinates[:, 2])
    method = "nearest" if nearest else "linear"
    interpolate = RegularGridInterpolator((x, y, z), field, method=method,
                                          bounds_error=False,
                                          fill_value=fill_value)
    # Get tissue elements values
    element_tags, element_coordinates = _get_tissue_elements(self, in_tissue)
    element_values = interpolate(element_coordinates)
    # Add the field
    add_anisotropy_from_elements(self, element_tags, element_values,
                                 in_tissue, fill_value, formula)
    return self


def add_anisotropy_from_nii(self, image_path, in_tissue, fill_value,
                            formula="1", nearest=False):
    """Add an anisotropic field to the model.

    Add an anisotropic field to the model based on a regular grid field
    contained in a `.nii` file.

    Parameters
    ----------
    image_path : str
        The path to the nifti file containing the field.
    in_tissue : str
        The name of the tissue to add anisotropy in.
    fill_value : float
        The value used in elements not included in `element_tags` but still in
        the same tissue.
    formula : str, optional
        The formula to compute the coefficient with. (The default is `1`).
    nearest : bool, optional
        If set to `True`, no linear interpolation is performed and the nearest
        value is used. (The default is `False`).

    Returns
    -------
    FEModel
        The current model.

    Raises
    ------
    KeyError
        If the tissue defined by `in_tissue` is not included in the model.
    ValueError
        If `field` contains neither a scalar field nor a vector field nor a
        tensor field or if the values are not in the last dimension.

    See Also
    --------
    add_anisotropy_from_elements
    add_anisotropy_from_array
    Anisotropy.evaluate_formula
    """
    image = nib.load(image_path)
    field = image.get_fdata()
    affine = image.affine
    add_anisotropy_from_array(self, field, affine, in_tissue,
                              fill_value, formula=formula,
                              nearest=nearest)
    return self


def _get_tissue_elements(self, name):
    gmsh.initialize()
    gmsh.open(self.mesh_path)
    element_type_tags = [(entity, *gmsh.model.mesh.getElements(3, entity)[:2])
                         for entity in self.tissues[name].volume_entity]
    element_tags = []
    element_coordinates = []
    for entity, types, tags in element_type_tags:
        for i, element_type in enumerate(types):
            element_tags.append(tags[i])
            element_coordinates.append(
                gmsh.model.mesh.getBarycenters(element_type, entity,
                                               False, False))
    gmsh.finalize()
    all_tags = np.hstack(element_tags)
    all_coordinates = np.hstack(element_coordinates).reshape((-1, 3))
    return all_tags, all_coordinates
