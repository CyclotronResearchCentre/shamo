"""Implement `Source` class.

This module implements the `Source` class which holds the data corresponding to
a source.
"""


class Source(dict):
    """Hold the data corresponding to a source.

    Parameters
    ----------
    coordinates : tuple (float, float, float)
        The coordinates of the source [mm].
    """

    def __init__(self, coordinates):
        if len(coordinates) != 3:
            raise ValueError("Argument 'coordinates' mus be of length 3.")
        self["coordinates"] = tuple([0.001 * c for c in coordinates])

    @property
    def coordinates(self):
        """Return the coordinates of the source.

        Returns
        -------
        tuple (float, float, float)
            The coordinates of the source.
        """
        return self["coordinates"]

    @property
    def x(self):
        """Return the coordinate of the source along x axis.

        Returns
        -------
        float
            The coordinate of the source along x axis.
        """
        return self["coordinates"][0]

    @property
    def y(self):
        """Return the coordinate of the source along y axis.

        Returns
        -------
        float
            The coordinate of the source along y axis.
        """
        return self["coordinates"][1]

    @property
    def z(self):
        """Return the coordinate of the source along z axis.

        Returns
        -------
        float
            The coordinate of the source along z axis.
        """
        return self["coordinates"][2]
