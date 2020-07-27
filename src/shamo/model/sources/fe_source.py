"""Implement `FESource` class.

This module implements the `FESource` class which holds the data corresponding
to a finite element source.
"""
from .source import Source


class FESource(Source):
    """Hold the data corresponding to a FE source.

    Parameters
    ----------
    coordinates : tuple (float, float, float)
        The coordinates of the source [mm].
    group : int
        The physical group of the source.
    point_groups : list [tuple (int, int)]
        The physical groups of the points.
    """

    def __init__(self, coordinates, length, group, point_groups):
        super().__init__(coordinates)
        self["length"] = float(length)
        self["group"] = int(group)
        self["point_groups"] = [tuple(axis) for axis in point_groups]

    @property
    def group(self):
        """Return the physical group of the source.

        Returns
        -------
        int
            The physical group of the source.
        """
        return self["group"]

    @property
    def length(self):
        """Return the length of the source along one axis.

        Returns
        -------
        float
            The length of the source along one axis.
        """
        return self["length"]

    @property
    def point_groups(self):
        """Return the physical groups of the points.

        Returns
        -------
        list [tuple (int, int)]
            The physical groups of the points.
        """
        return self["point_groups"]

    @property
    def px(self):
        """Return the physical groups of the points along x axis.

        Returns
        -------
        tuple (int, int)
            The physical groups of the points along x axis.
        """
        return self["point_groups"][0]

    @property
    def py(self):
        """Return the physical groups of the points along y axis.

        Returns
        -------
        tuple (int, int)
            The physical groups of the points along y axis.
        """
        return self["point_groups"][1]

    @property
    def pz(self):
        """Return the physical groups of the points along z axis.

        Returns
        -------
        tuple (int, int)
            The physical groups of the points along z axis.
        """
        return self["point_groups"][2]
