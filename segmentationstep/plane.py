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
import sys
print(sys.path)
from math import sqrt

from segmentationstep.math.algorithms import CentroidAlgorithm
from segmentationstep.math.vectorops import add, dot, mult, sub
from segmentationstep.misc import checkRange

class Plane(object):

    def __init__(self, fieldmodule):
        self._normal_field = self._createNormalField(fieldmodule)
        self._rotation_point_field = self._createRotationPointField(fieldmodule)
        self._centre_point_field = self._createRotationPointField(fieldmodule)
        self._dimensions = [1, 1, 1]

    def setDimensions(self, dimensions):
        self._dimensions = dimensions

    def getDimensions(self):
        return self._dimensions

    def getRegion(self):
        return self._normal_field.getFieldmodule().getRegion()

    def _createNormalField(self, fieldmodule):
        plane_normal_field = fieldmodule.createFieldConstant([1, 0, 0])
        return plane_normal_field

    def _createRotationPointField(self, fieldmodule):
        point_on_plane_field = fieldmodule.createFieldConstant([0, 0, 0])
        return point_on_plane_field

    def setPlaneEquation(self, normal, point):
        fieldmodule = self._normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._normal_field.assignReal(fieldcache, normal)
        self._rotation_point_field.assignReal(fieldcache, point)
        fieldmodule.endChange()

    def getNormalField(self):
        return self._normal_field

    def getRotationPointField(self):
        return self._rotation_point_field

    def getNormal(self):
        fieldmodule = self._normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, normal = self._normal_field.evaluateReal(fieldcache, 3)

        return normal

    def setNormal(self, normal):
        fieldmodule = self._normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._normal_field.assignReal(fieldcache, normal)
        fieldmodule.endChange()

    def setRotationPoint(self, point):
        fieldmodule = self._rotation_point_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._rotation_point_field.assignReal(fieldcache, point)
        fieldmodule.endChange()

    def getRotationPoint(self):
        fieldmodule = self._rotation_point_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, point = self._rotation_point_field.evaluateReal(fieldcache, 3)

        return point

    def calcluateIntersection(self, pt1, pt2):
        point_on_plane = self.getRotationPoint()  # self._plane_centre_position  # self._getPointOnPlane()
        plane_normal = self.getNormal()

#         x, y = self._ui._sceneviewer3d.mapToWidget(x, y)
#         far_plane_point = self._ui._sceneviewer3d.unproject(x, -y, -1.0)
#         near_plane_point = self._ui._sceneviewer3d.unproject(x, -y, 1.0)
        line_direction = sub(pt2, pt1)
        d = dot(sub(point_on_plane, pt1), plane_normal) / dot(line_direction, plane_normal)
        intersection_point = add(mult(line_direction, d), pt1)
        if abs(dot(sub(point_on_plane, intersection_point), plane_normal)) < 1e-08:
            return intersection_point

        return None

    def calculatePlaneCentre(self):
        tol = 1e-08
        dim = self.getDimensions()
        plane_normal = self.getNormal()
        point_on_plane = self.getRotationPoint()
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

        if self._debug_print:
            print
            print(ipts)
            print(unique_ipts)

        ca = CentroidAlgorithm(unique_ipts)
#         wa = WeiszfeldsAlgorithm(unique_ipts)
        plane_centre = ca.compute()
        return plane_centre


class PlaneMovement(object):

    def __init__(self, mode):
        self._mode = mode
        self._active = False
        self._selectionfilter = None
        self._set_selection_filter_method = None

    def isActive(self):
        return self._active

    def mode(self):
        return self._mode

    def setSelectionFilter(self, selectionfilter):
        self._selectionfilter = selectionfilter

    def setSelectionFilterMethod(self, selectionfilter_method):
        self._set_selection_filter_method = selectionfilter_method

    def leave(self):
        pass

    def enter(self):
        if self._set_selection_filter_method and self._selectionfilter:
            self._set_selection_filter_method(self._selectionfilter)


class PlaneMovementGlyph(PlaneMovement):

    def __init__(self, mode):
        super(PlaneMovementGlyph, self).__init__(mode)
        self._default_material = None
        self._active_material = None
        self._glyph = None

    def setDefaultMaterial(self, material):
        self._default_material = material

    def setActiveMaterial(self, material):
        self._active_material = material

    def setActive(self, active=True):
        self._active = active
        if self._glyph and active:
            self._glyph.setMaterial(self._active_material)
        elif self._glyph and not active:
            self._glyph.setMaterial(self._default_material)

    def setGlyph(self, glyph):
        self._glyph = glyph

    def enter(self):
        super(PlaneMovementGlyph, self).enter()
        self.setActive(False)
        self._glyph.setVisibilityFlag(True)

    def leave(self):
        super(PlaneMovementGlyph, self).leave()
        self.setActive(False)
        self._glyph.setVisibilityFlag(False)


