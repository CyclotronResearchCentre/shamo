"""Provide geometric utilities."""
import numpy as np


class Plane3D:
    """A 3D plane.

    Parameters
    ----------
    p0 : 3D Coords
        The first point of the plane. This point will serve as the origin of the
        coordinates system.
    p1 : 3D Coords
        A second point.
    p2 : 3D Coords
        A third point.
    """

    def __init__(self, orig, eig1, eig2) -> None:
        # Set origin
        self.o = np.array(orig)
        # Set eigen vectors
        _e1, _e2 = np.array(eig1), np.array(eig2)
        self.e1 = _e1 / np.linalg.norm(_e1)
        self.e2 = _e2 / np.linalg.norm(_e2)
        # Set normal
        self.n = np.cross(self.e1, self.e2)

    def dist(self, points):
        """Return the orthogonal distances from a set of points to the plane."""
        return np.apply_along_axis(lambda p: (p - self.o) @ self.n, 1, points)

    def abs_dist(self, points):
        """Return the absolute distance from a set of points to the plane."""
        return np.abs(self.dist(points))

    def to_2d(self, points):
        """Return the orthogonal projection 2D coordinates of a set of points."""
        points = np.array(points)
        to_orig = lambda p: p - self.o
        return np.apply_along_axis(
            lambda p: (to_orig(p) @ self.e1, to_orig(p) @ self.e2), 1, points
        )

    def to_3d(self, points, dist):
        """Return a 3D orthogonal projection of the plane points into the 3D space."""
        points = np.array(points)
        return self.o + points[:, 0] * self.e1 + points[:, 1] * self.e2 + dist * self.n
