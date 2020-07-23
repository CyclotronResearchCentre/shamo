"""Implement the `MeshConfig` class.

This module implements the `MeshConfig` class which is used when generating a
`FEModel`.
"""


class MeshConfig(dict):
    """Provide the settings for a mesh generation.

    Parameters
    ----------
    cell_size : float
        The size of the cells.
    facet_size : float
        The size of the facets.
    facet_angle : float
        The angle of the faces.
    facet_distance : float
        The distance from the facets.
    cell_radius_edge_ratio : float
        The ratio between cell radius and edges.

    See Also
    --------
    pygalmesh.generate_from_inr
        The attributes of are passed to this function.
    """

    def __init__(
        self,
        cell_size=0.0,
        edge_size=0.0,
        facet_size=0.0,
        facet_angle=0.0,
        facet_distance=0.0,
        cell_radius_edge_ratio=0.0,
    ):
        super().__init__()
        self["cell_size"] = float(cell_size)
        self["edge_size"] = float(edge_size)
        self["facet_size"] = float(facet_size)
        self["facet_angle"] = float(facet_angle)
        self["facet_distance"] = float(facet_distance)
        self["cell_radius_edge_ratio"] = float(cell_radius_edge_ratio)

    @property
    def cell_radius_edge_ratio(self):
        """Return the cell radius to edge ratio.

        Returns
        -------
        float
            The cell radius to edge ratio.
        """
        return self["cell_radius_edge_ratio"]

    @cell_radius_edge_ratio.setter
    def cell_radius_edge_ratio(self, new_cell_radius_edge_ratio):
        """Set the cell radius to edge ratio."""
        self["cell_radius_edge_ratio"] = new_cell_radius_edge_ratio

    @property
    def cell_size(self):
        """Return the cell size.

        Returns
        -------
        float
            The cell size.
        """
        return self["cell_size"]

    @cell_size.setter
    def cell_size(self, new_cell_size):
        """Set the cell size."""
        self["cell_size"] = new_cell_size

    @property
    def edge_size(self):
        """Return the edge size.

        Returns
        -------
        float
            The edge size.
        """
        return self["edge_size"]

    @edge_size.setter
    def edge_size(self, new_edge_size):
        """Set the edge size."""
        self["edge_size"] = new_edge_size

    @property
    def facet_angle(self):
        """Return the facet angle.

        Returns
        -------
        float
            The facet angle.
        """
        return self["facet_angle"]

    @facet_angle.setter
    def facet_angle(self, new_facet_angle):
        """Set the facet angle."""
        self["facet_angle"] = new_facet_angle

    @property
    def facet_distance(self):
        """Return the facet distance.

        Returns
        -------
        float
            The facet distance.
        """
        return self["facet_distance"]

    @facet_distance.setter
    def facet_distance(self, new_facet_distance):
        """Set the facet distance."""
        self["facet_distance"] = new_facet_distance

    @property
    def facet_size(self):
        """Return the facet size.

        Returns
        -------
        float
            The facet size.
        """
        return self["facet_size"]

    @facet_size.setter
    def facet_size(self, new_facet_size):
        """Set the facet size."""
        self["facet_size"] = new_facet_size
