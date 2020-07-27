"""Implement `EEGSource` class.

This module implements the `EEGSource` class which holds the data corresponding
to a source.
"""
import numpy as np

from .source import Source


class EEGSource(Source):
    """Hold the data corresponding to an EEG source.

    Parameters
    ----------
    coordinates : tuple (float, float, float)
        The coordinates of the source [mm].
    orientation : tuple (float, float, float)
        The orientation of the source.
    value : float
        The dipole moment of the source [Am].
    """

    def __init__(self, coordinates, orientation, value):
        super().__init__(coordinates)
        if len(orientation) != 3:
            raise ValueError("Argument 'orientation' mus be of length 3.")
        self["orientation"] = tuple(orientation)
        self["value"] = float(value)
        # Compute unitary orientation
        self["unit_orientation"] = tuple(
            np.array(orientation) / np.linalg.norm(orientation)
        )

    @property
    def orientation(self):
        """Return the orientation of the source.

        Returns
        -------
        tuple (float, float, float)
            The orientation of the source.
        """
        return self["orientation"]

    @property
    def dx(self):
        """Return the orientation of the source along x axis.

        Returns
        -------
        float
            The orientation of the source along x axis.
        """
        return self["orientation"][0]

    @property
    def dy(self):
        """Return the orientation of the source along y axis.

        Returns
        -------
        float
            The orientation of the source along y axis.
        """
        return self["orientation"][1]

    @property
    def dz(self):
        """Return the orientation of the source along z axis.

        Returns
        -------
        float
            The orientation of the source along z axis.
        """
        return self["orientation"][2]

    @property
    def value(self):
        """Return the dipole moment of the source [Am].

        Returns
        -------
        float
            The dipole moment of the source [Am].
        """
        return self["value"]

    @property
    def unit_orientation(self):
        """Return the unitary orientation of the source.

        Returns
        -------
        tuple (float, float, float)
            The unitary orientation of the source.
        """
        return self["unit_orientation"]

    @property
    def values(self):
        """Return the values along each axis.

        Returns
        -------
        numpy.ndarray
            The values along each axis.
        """
        return np.array(self.unit_orientation) * self.value
