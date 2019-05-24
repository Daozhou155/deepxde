from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from . import geometry


class CSGUnion(geometry.Geometry):
    """Construct an object by CSG Union."""

    def __init__(self, geom1, geom2):
        if geom1.dim != geom2.dim:
            raise ValueError(
                "{} + {} failed (dimensions do not match).".format(
                    geom1.idstr, geom2.idstr
                )
            )
        super(CSGUnion, self).__init__(geom1.dim, geom1.diam)
        self.geom1 = geom1
        self.geom2 = geom2

    def inside(self, x):
        return self.geom1.inside(x) or self.geom2.inside(x)

    def on_boundary(self, x):
        return (self.geom1.on_boundary(x) and not self.geom2.inside(x)) or (
            self.geom2.on_boundary(x) and not self.geom1.inside(x)
        )

    def boundary_normal(self, x):
        if self.geom1.on_boundary(x) and not self.geom2.inside(x):
            return self.geom1.boundary_normal(x)
        if self.geom2.on_boundary(x) and not self.geom1.inside(x):
            return self.geom2.boundary_normal(x)
        return np.zeros(self.dim)

    def random_points(self, n, random="pseudo"):
        # TODO: Use bounding box to ensure uniform random
        x = np.array(
            [
                x
                for x in self.geom1.random_points(n, random=random)
                if not self.geom2.inside(x)
            ]
        )
        x = np.vstack((x, self.geom2.random_points(n, random=random)))
        if n != len(x):
            print(
                "Warning: {} points required, but {} points sampled. Uniform random is not guaranteed.".format(
                    n, len(x)
                )
            )
        return x

    def random_boundary_points(self, n, random="pseudo"):
        x = [
            x
            for x in self.geom1.random_boundary_points(n, random=random)
            if not self.geom2.inside(x)
        ]
        x += [
            x
            for x in self.geom2.random_boundary_points(n, random=random)
            if not self.geom1.inside(x)
        ]
        if n != len(x):
            print(
                "Warning: {} points required, but {} points sampled. Uniform random is not guaranteed.".format(
                    n, len(x)
                )
            )
        return np.array(x)

    def periodic_point(self, x, component):
        if self.geom1.on_boundary(x) and not self.geom2.inside(x):
            y = self.geom1.periodic_point(x, component)
            if self.on_boundary(y):
                return y
        if self.geom2.on_boundary(x) and not self.geom1.inside(x):
            y = self.geom2.periodic_point(x, component)
            if self.on_boundary(y):
                return y
        return x


class CSGDifference(geometry.Geometry):
    """Construct an object by CSG Difference."""

    def __init__(self, geom1, geom2):
        if geom1.dim != geom2.dim:
            raise ValueError(
                "{} - {} failed (dimensions do not match).".format(
                    geom1.idstr, geom2.idstr
                )
            )
        super(CSGDifference, self).__init__(geom1.dim, geom1.diam)
        self.geom1 = geom1
        self.geom2 = geom2

    def inside(self, x):
        return self.geom1.inside(x) and not self.geom2.inside(x)

    def on_boundary(self, x):
        return (self.geom1.on_boundary(x) and not self.geom2.inside(x)) or (
            self.geom1.inside(x) and self.geom2.on_boundary(x)
        )

    def boundary_normal(self, x):
        if self.geom1.on_boundary(x) and not self.geom2.inside(x):
            return self.geom1.boundary_normal(x)
        if self.geom1.inside(x) and self.geom2.on_boundary(x):
            return -self.geom2.boundary_normal(x)
        return np.zeros(self.dim)

    def random_points(self, n, random="pseudo"):
        x = []
        while len(x) < n:
            x += [
                x
                for x in self.geom1.random_points(n, random=random)
                if not self.geom2.inside(x)
            ]
        return np.array(x[:n])

    def random_boundary_points(self, n, random="pseudo"):
        x1 = [
            x
            for x in self.geom1.random_boundary_points(n, random=random)
            if not self.geom2.inside(x)
        ]
        x2 = [
            x
            for x in self.geom2.random_boundary_points(n, random=random)
            if self.geom1.inside(x)
        ]
        x = x1 + x2
        if n != len(x):
            print(
                "Warning: {} points required, but {} points sampled. Uniform random is not guaranteed.".format(
                    n, len(x)
                )
            )
        return np.array(x)

    def periodic_point(self, x, component):
        if self.geom1.on_boundary(x) and not self.geom2.inside(x):
            y = self.geom1.periodic_point(x, component)
            if self.on_boundary(y):
                return y
        return x
