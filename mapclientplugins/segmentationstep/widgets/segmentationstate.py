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

from mapclientplugins.segmentationstep.widgets.definitions import DEFAULT_NORMAL_ARROW_SIZE, DEFAULT_GRAPHICS_SPHERE_SIZE
from mapclientplugins.segmentationstep.widgets.zincwidget import ProjectionMode

class SegmentationState(object):

    def __init__(self):
        self._eye = None
        self._lookat = None
        self._up = None
        self._pop = None
        self._normal = None
        self._rotation_mode = None
        self._projection_mode = ProjectionMode.PERSPECTIVE
        self._normal_base_size = DEFAULT_NORMAL_ARROW_SIZE
        self._rotation_centre_base_size = DEFAULT_GRAPHICS_SPHERE_SIZE

    def setViewParameters(self, eye, lookat, up):
        self._eye = eye
        self._lookat = lookat
        self._up = up

    def getViewParameters(self):
        return self._eye, self._lookat, self._up

    def setPointOnPlane(self, pt):
        self._pop = pt

    def getPointOnPlane(self):
        return self._pop

    def setPlaneNormal(self, normal):
        self._normal = normal

    def getPlaneNormal(self):
        return self._normal

    def setPlaneRotationMode(self, mode):
        self._rotation_mode = mode

    def getPlaneRotationMode(self):
        return self._rotation_mode

    def setProjectionMode(self, mode):
        self._projection_mode = mode

    def getProjectionMode(self):
        return self._projection_mode

    def setPlaneNormalGlyphBaseSize(self, base_size):
        self._normal_base_size = base_size

    def getPlaneNormalGlyphBaseSize(self):
        return self._normal_base_size

    def setPlaneRotationCentreGlyphBaseSize(self, base_size):
        self._rotation_centre_base_size = base_size

    def getPlaneRotationCentreGlyphBaseSize(self):
        return self._rotation_centre_base_size

