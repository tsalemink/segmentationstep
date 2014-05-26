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
from mapclientplugins.segmentationstep.observed import event

class Plane(object):

    def __init__(self, fieldmodule):
        self._normal_field = self._createNormalField(fieldmodule)
        self._rotation_point_field = self._createRotationPointField(fieldmodule)
        self._centre_point_field = self._createRotationPointField(fieldmodule)

    def _createNormalField(self, fieldmodule):
        plane_normal_field = fieldmodule.createFieldConstant([1, 0, 0])
        return plane_normal_field

    def _createRotationPointField(self, fieldmodule):
        point_on_plane_field = fieldmodule.createFieldConstant([0, 0, 0])
        return point_on_plane_field

    @event
    def notifyChange(self):
        '''
        Using this as an event notification call.
        '''
        pass

    def getRegion(self):
        return self._normal_field.getFieldmodule().getRegion()

    def getNormalField(self):
        return self._normal_field

    def getRotationPointField(self):
        return self._rotation_point_field

    def getNormal(self):
        fieldmodule = self._normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, normal = self._normal_field.evaluateReal(fieldcache, 3)

        return normal

    def getRotationPoint(self):
        fieldmodule = self._rotation_point_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, point = self._rotation_point_field.evaluateReal(fieldcache, 3)

        return point

    def setPlaneEquation(self, normal, point):
        fieldmodule = self._normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._normal_field.assignReal(fieldcache, normal)
        self._rotation_point_field.assignReal(fieldcache, point)
        fieldmodule.endChange()
        self.notifyChange()

    def setNormal(self, normal):
        fieldmodule = self._normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._normal_field.assignReal(fieldcache, normal)
        fieldmodule.endChange()
        self.notifyChange()

    def setRotationPoint(self, point):
        fieldmodule = self._rotation_point_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._rotation_point_field.assignReal(fieldcache, point)
        fieldmodule.endChange()
        self.notifyChange()

    def getAttitude(self):
        pa = PlaneAttitude(self.getRotationPoint(), self.getNormal())
        return pa


class PlaneAttitude(object):

    prec = 12

    def __init__(self, point, normal):
        self._normal = normal
        self._point = point

    def getNormal(self):
        return self._normal

    def getPoint(self):
        return self._point

    def __hash__(self, *args, **kwargs):
        p = [str(int(v * (10 ** self.prec))) for v in self._point]
        n = [str(int(v * (10 ** self.prec))) for v in self._normal]
        str_repr = ''.join(p) + ''.join(n)
        return hash(str_repr)

    def __eq__(self, other):
        return hash(self) == hash(other)


