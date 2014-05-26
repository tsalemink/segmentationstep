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

from math import cos, sin, sqrt, acos, pi

from mapclientplugins.segmentationstep.viewmodes.glyphmode import GlyphMode
from mapclientplugins.segmentationstep.widgets.definitions import ViewMode
from mapclientplugins.segmentationstep.maths.vectorops import add, mult, cross, dot, sub, normalize
from mapclientplugins.segmentationstep.maths.algorithms import calculateCentroid, boundCoordinatesToCuboid, calculateLinePlaneIntersection
from mapclientplugins.segmentationstep.zincutils import getGlyphPosition, setGlyphPosition, createPlaneManipulationSphere

class RotationMode(GlyphMode):
    '''
    Handle sceneviewer input events when in rotation mode.
    The rotation mode allows the user to re-orient the image
    plane and set the plane point of rotation.
    '''
    def __init__(self, plane, undo_redo_stack):
        super(RotationMode, self).__init__(plane, undo_redo_stack)
        self._mode_type = ViewMode.PLANE_ROTATION
        self._glyph = createPlaneManipulationSphere(plane.getRegion())
        self._width_method = None
        self._height_method = None
        self._getViewParameters_method = None

    def setWidthHeightMethods(self, width_method, height_method):
        self._width_method = width_method
        self._height_method = height_method

    def setGetViewParametersMethod(self, get_view_parameters_method):
        self._getViewParameters_method = get_view_parameters_method

    def mousePressEvent(self, mouseevent):
        super(RotationMode, self).mousePressEvent(mouseevent)

    def mouseMoveEvent(self, mouseevent):
        scene = self._glyph.getScene()
        scene.beginChange()
        super(RotationMode, self).mouseMoveEvent(mouseevent)
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            x = mouseevent.x()
            y = mouseevent.y()
            far_plane_point = self._unproject_method(x, -y, -1.0)
            near_plane_point = self._unproject_method(x, -y, 1.0)
            point_on_plane = calculateLinePlaneIntersection(near_plane_point, far_plane_point, self._plane.getRotationPoint(), self._plane.getNormal())
            if point_on_plane is not None:
                dimensions = self._get_dimension_method()
                centroid = calculateCentroid(self._plane.getRotationPoint(), self._plane.getNormal(), dimensions)
                point_on_plane = boundCoordinatesToCuboid(point_on_plane, centroid, dimensions)
                setGlyphPosition(self._glyph, point_on_plane)
        else:
            width = self._width_method()
            height = self._height_method()
            radius = min([width, height]) / 2.0
            delta_x = float(mouseevent.x() - self._previous_mouse_position[0])
            delta_y = float(mouseevent.y() - self._previous_mouse_position[1])
            tangent_dist = sqrt((delta_x * delta_x + delta_y * delta_y))
            if tangent_dist > 0.0:
                dx = -delta_y / tangent_dist;
                dy = delta_x / tangent_dist;

                d = dx * (mouseevent.x() - 0.5 * (width - 1)) + dy * ((mouseevent.y() - 0.5 * (height - 1)))
                if d > radius: d = radius
                if d < -radius: d = -radius

                phi = acos(d / radius) - 0.5 * pi
                angle = 1.0 * tangent_dist / radius

                eye, lookat, up, _ = self._getViewParameters_method()

                b = up[:]
                b = normalize(b)
                a = sub(lookat, eye)
                a = normalize(a)
                c = cross(b, a)
                c = normalize(c)
                e = [None, None, None]
                e[0] = dx * c[0] + dy * b[0]
                e[1] = dx * c[1] + dy * b[1]
                e[2] = dx * c[2] + dy * b[2]
                axis = [None, None, None]
                axis[0] = sin(phi) * a[0] + cos(phi) * e[0]
                axis[1] = sin(phi) * a[1] + cos(phi) * e[1]
                axis[2] = sin(phi) * a[2] + cos(phi) * e[2]

                plane_normal = self._plane.getNormal()
                point_on_plane = self._plane.getRotationPoint()

                plane_normal_prime_1 = mult(plane_normal, cos(angle))
                plane_normal_prime_2 = mult(plane_normal, dot(plane_normal, axis) * (1 - cos(angle)))
                plane_normal_prime_3 = mult(cross(axis, plane_normal), sin(angle))
                plane_normal_prime = add(add(plane_normal_prime_1, plane_normal_prime_2), plane_normal_prime_3)

                self._plane.setPlaneEquation(plane_normal_prime, point_on_plane)

                self._previous_mouse_position = [mouseevent.x(), mouseevent.y()]
        scene.endChange()

    def mouseReleaseEvent(self, mouseevent):
        scene = self._glyph.getScene()
        scene.beginChange()
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            point_on_plane = getGlyphPosition(self._glyph)
            self._plane.setRotationPoint(point_on_plane)

        super(RotationMode, self).mouseReleaseEvent(mouseevent)
        scene.endChange()

        self.setUndoRedoCommand('plane rotation')


    def enter(self):
        scene = self._glyph.getScene()
        scene.beginChange()
        super(RotationMode, self).enter()
        setGlyphPosition(self._glyph, self._plane.getRotationPoint())
        scene.endChange()


