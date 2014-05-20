'''
MAP Client, a program to generate detailed musculoskeletal models for OpenSim.
    Copyright (C) 2012  University of Auckland
    
This file is part of MAP Client. (http://launchpad.net/mapclient)

    MAP Client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MAP Client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MAP Client.  If not, see <http://www.gnu.org/licenses/>..
'''
from math import atan2, pi, sqrt, copysign

from mapclientplugins.segmentationstep.maths.vectorops import add, cross, div, dot, normalize, sub, mult
from mapclientplugins.segmentationstep.misc import checkRange

def boundCoordinatesToCuboid(pt1, pt2, cuboid_dimensions):
    '''
    Takes two points and a cuboids dimensions, with 
    one corner defined by [0, 0, 0] and the opposite by 
    cuboid_dimensions, and returns a point that is inside the 
    cuboid.  pt2 *must* be inside the cuboid.
    '''
    bounded_pt = pt1[:]
    axes = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    coordinate_set = [[0, 0, 0], [cuboid_dimensions[0], cuboid_dimensions[1], cuboid_dimensions[2]]]
    outside = [False, False, False]

    for i, axis in enumerate(axes):
        v1 = sub(pt1, coordinate_set[0])
        v2 = sub(pt1, coordinate_set[1])
        dir1 = dot(v1, axis)
        dir2 = dot(v2, axis)
        if copysign(1, dir1) == copysign(1, dir2):
            if copysign(1, dir1) < 0:
                outside[i] = 1
            else:
                outside[i] = 2

    if any(outside):
        indices = [i for i, x in enumerate(outside) if x]
        ipt = None
        for index in indices:
            if outside[index] == 1:
                ipt = calculateLinePlaneIntersection(pt1, pt2, coordinate_set[0], axes[index])
            else:
                ipt = calculateLinePlaneIntersection(pt1, pt2, coordinate_set[1], axes[index])

            ipt_0 = checkRange(ipt[0], coordinate_set[0][0], coordinate_set[1][0])
            ipt_1 = checkRange(ipt[1], coordinate_set[0][1], coordinate_set[1][1])
            ipt_2 = checkRange(ipt[2], coordinate_set[0][2], coordinate_set[1][2])

            if ipt_0 and ipt_1 and ipt_2:
                bounded_pt = ipt

    return bounded_pt

def pointOutsideCuboid(pt, cuboid_dimensions):
    '''
    Determine if the given point is outside the cuboid and 
    return a number determining which planes it is outside of.
    0 indicates that the pt is inside the cuboid.
    '''
    outside = 0

    axes = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    coordinate_set = [[0, 0, 0], [cuboid_dimensions[0], cuboid_dimensions[1], cuboid_dimensions[2]]]
    for i, axis in enumerate(axes):
        v1 = sub(pt, coordinate_set[0])
        v2 = sub(pt, coordinate_set[1])
        dir1 = dot(v1, axis)
        dir2 = dot(v2, axis)
        if copysign(1, dir1) == copysign(1, dir2):
            if copysign(1, dir1) < 0:
                outside += 2 ** (2 * i)
            else:
                outside += 2 ** (2 * i + 1)

    return outside

def calculateLinePlaneIntersection(pt1, pt2, point_on_plane, plane_normal):
    line_direction = sub(pt2, pt1)
    d = dot(sub(point_on_plane, pt1), plane_normal) / dot(line_direction, plane_normal)
    intersection_point = add(mult(line_direction, d), pt1)
    if abs(dot(sub(point_on_plane, intersection_point), plane_normal)) < 1e-08:
        return intersection_point

    return None

def calculateCentroid(point_on_plane, plane_normal, cuboid_dimensions):
    '''
    Takes a description of a plane as a point on the plane 
    and a normal of the plane with a cuboids dimensions, with 
    one corner defined by [0, 0, 0] and the opposite by 
    cuboid_dimensions, and calculates the centroid formed by the
    given plane intersecting with the cuboid.
    '''
    tol = 1e-08
    dim = cuboid_dimensions
#         print(point_on_plane, plane_normal)
    axes = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    coordinate_set = [[0, 0, 0], [dim[0], 0, 0], [0, dim[1], 0], [dim[0], dim[1], 0], [0, 0, dim[2]], [dim[0], 0, dim[2]], [0, dim[1], dim[2]], [dim[0], dim[1], dim[2]]]

    ipts = []
    for axis in axes:
        den = dot(axis, plane_normal)
        if abs(den) < tol:
            continue

        for corner in coordinate_set:
            num = dot(sub(point_on_plane, corner), plane_normal)
            d = num / den

            ipt = add(mult(axis, d), corner)
            # check if all intersections are valid, taking care to be aware of minus signs.
            ipt_0 = checkRange(ipt[0], 0.0, dim[0])
            ipt_1 = checkRange(ipt[1], 0.0, dim[1])
            ipt_2 = checkRange(ipt[2], 0.0, dim[2])

            if ipt_0 and ipt_1 and ipt_2:
                ipts.append(ipt)

    unique_ipts = []
    for p in ipts:
        insert = True
        for u in unique_ipts:
            vdiff = sub(p, u)
            if sqrt(dot(vdiff, vdiff)) < tol:
                insert = False
        if insert:
            unique_ipts.append(p)

    ca = CentroidAlgorithm(unique_ipts)
#         wa = WeiszfeldsAlgorithm(unique_ipts)
    plane_centre = ca.compute()
    return plane_centre

class CentroidAlgorithm(object):

    def __init__(self, xi):
        self._xi = xi

    def compute(self):
        if len(self._xi) == 0:
            return None

        ave = self._average()
        e1, e2, e3 = self._calculateBasis()
        trans_xi = self._convertXi(ave, e1, e2, e3)
        ordered_xi = self._orderByHeading(trans_xi)
        area = self._calculatePolygonArea(ordered_xi)
        cx, cy = self._calculateCxCy(ordered_xi, area)
        centroid_x = ave[0] + e1[0] * cx + e2[0] * cy
        centroid_y = ave[1] + e1[1] * cx + e2[1] * cy
        centroid_z = ave[2] + e1[2] * cx + e2[2] * cy
        centroid = [centroid_x, centroid_y, centroid_z]

        return centroid

    def _orderByHeading(self, trans_xi):
        headings = self._calculateHeading(trans_xi)
        heading_indexes = [i[0] for i in sorted(enumerate(headings), key=lambda x:x[1])]
        ordered_xi = [trans_xi[i] for i in heading_indexes]
        ordered_xi.append(ordered_xi[0])  # repeat the first vertex

        return ordered_xi

    def _calculateCxCy(self, vertices, area):
        cx = 0.0
        cy = 0.0
        for i in range(len(vertices) - 1):
            val = (vertices[i][0] * vertices[i + 1][1] - vertices[i + 1][0] * vertices[i][1])
            cx += ((vertices[i][0] + vertices[i + 1][0]) * val)
            cy += ((vertices[i][1] + vertices[i + 1][1]) * val)

        cx = cx / (6 * area)
        cy = cy / (6 * area)
        return cx, cy

    def _calculatePolygonArea(self, vertices):
        area = 0.0
        for i in range(len(vertices) - 1):
            area += (vertices[i][0] * vertices[i + 1][1] - vertices[i + 1][0] * vertices[i][1])
        return 0.5 * area

    def _calculateHeading(self, direction):
        '''
        Convert a vector based direction into a heading
        between 0 and 2*pi.
        '''
        headings = [atan2(pt[1], pt[0]) + pi for pt in direction]
        return headings

    def _calculateBasis(self):
        e1 = e2 = e3 = None
        if len(self._xi) > 2:
            pta = self._xi[0]
            ptb = self._xi[1]
            ptc = self._xi[2]
            e1 = sub(ptb, pta)
            e2 = sub(ptc, pta)
#             e2 = cross(e1, self._nor)
            e3 = cross(e1, e2)
            e2 = cross(e1, e3)
            e1 = normalize(e1)
            e2 = normalize(e2)
            e3 = normalize(e3)

        return e1, e2, e3

    def _convertXi(self, ori, e1, e2, e3):
        '''
        Use average point as the origin 
        for new basis.
        '''
        converted = []

        for v in self._xi:
            diff = sub(v, ori)
            bv = [dot(diff, e1), dot(diff, e2)]
            converted.append(bv)

        return converted

    def _average(self):
        sum_xi = None
        for v in self._xi:
            if not sum_xi:
                sum_xi = [0.0] * len(v)
            sum_xi = add(sum_xi, v)

        average = div(sum_xi, len(self._xi))
        return average

class WeiszfeldsAlgorithm(object):

    def __init__(self, xi):

        self._xi = xi
        self._eps = 1e-04

    def compute(self):
        init_yi = self._average()
        yi = init_yi
        converged = False
        it = 0
        while not converged:

            diffi = [sub(xj, yi) for xj in self._xi]
            normi = [sqrt(dot(di, di)) for di in diffi]
            weight = sum([1 / ni for ni in normi])
            val = [div(self._xi[i], normi[i]) for i in range(len(self._xi))]

            yip1 = self._weightedaverage(val, weight)
            diff = sub(yip1, yi)
            yi = yip1
            it += 1
#             print(it)
            if sqrt(dot(diff, diff)) < self._eps:
                converged = True

        return yi

    def _weightedaverage(self, values, weight):
        sum_values = None
        for v in values:
            if not sum_values:
                sum_values = [0.0] * len(v)
            sum_values = add(sum_values, v)

        weightedaverage = div(sum_values, weight)
        return weightedaverage

    def _average(self):
        sum_xi = None
        for v in self._xi:
            if not sum_xi:
                sum_xi = [0.0] * len(v)
            sum_xi = add(sum_xi, v)

        average = div(sum_xi, len(self._xi))
        return average
