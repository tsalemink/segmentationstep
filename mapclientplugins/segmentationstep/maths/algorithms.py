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

from math import atan2, pi, sqrt
from mapclientplugins.segmentationstep.maths.vectorops import add, cross, div, dot, normalize, sub

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
