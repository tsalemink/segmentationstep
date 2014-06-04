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
from math import cos, sin, acos, copysign

from PySide import QtCore

from mapclientplugins.segmentationstep.maths.vectorops import add, mult, cross, dot, sub, normalize, magnitude
from mapclientplugins.segmentationstep.maths.algorithms import calculateCentroid
from mapclientplugins.segmentationstep.undoredo import CommandChangeView
from mapclientplugins.segmentationstep.definitions import IMAGE_PLANE_GRAPHIC_NAME, POINT_CLOUD_ON_PLANE_GRAPHIC_NAME, SELECTION_BOX_2D_GRAPHIC_NAME, \
    CURVE_ON_PLANE_GRAPHIC_NAME
from mapclientplugins.segmentationstep.zincutils import createSelectionBox

class Abstract2DHandler(object):

    def __init__(self, plane, undo_redo_stack):
        super(Abstract2DHandler, self).__init__(plane, undo_redo_stack)
        self._selection_box = createSelectionBox(plane.getRegion(), SELECTION_BOX_2D_GRAPHIC_NAME)

    def mousePressEvent(self, event):
        self._start_position = None
        if not event.modifiers() and event.button() == QtCore.Qt.LeftButton:
            self._start_position = [event.x(), event.y()]
            self._start_view_parameters = self._zinc_view.getViewParameters()
        else:
            super(Abstract2DHandler, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._start_position is not None:
            # v_rot = v*cos(theta)+(wxv)*sin(theta)+w*(w.v)*(1-cos(theta))
            # v is our vector
            # w is the unit vector to rotate around
            # theta is the angle to rotate
            if self._start_position[0] == event.x() and self._start_position[1] == event.y():
                return
            centre_point = calculateCentroid(self._plane.getRotationPoint(), self._plane.getNormal(), self._get_dimension_method())
            centre_widget = self._zinc_view.project(centre_point[0], centre_point[1], centre_point[2])
            a = sub(centre_widget, [event.x(), -event.y(), centre_widget[2]])
            b = sub(centre_widget, [self._start_position[0], -self._start_position[1], centre_widget[2]])
            c = dot(a, b)
            d = magnitude(a) * magnitude(b)
            theta = acos(min(c / d, 1.0))
            if theta != 0.0:
                g = cross(a, b)
                lookat, eye, up, angle = self._zinc_view.getViewParameters()
                w = normalize(sub(lookat, eye))
                if copysign(1, dot(g, [0, 0, 1])) < 0:
                    theta = -theta
                v = up
                p1 = mult(v, cos(theta))
                p2 = mult(cross(w, v), sin(theta))
                p3a = mult(w, dot(w, v))
                p3 = mult(p3a, 1 - cos(theta))
                v_rot = add(p1, add(p2, p3))
                self._zinc_view.setViewParameters(lookat, eye, v_rot, angle)
                self._start_position = [event.x(), event.y()]
        else:
            super(Abstract2DHandler, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._start_position is not None:
            # Do undo redo command
            end_view_parameters = self._zinc_view.getViewParameters()
            c = CommandChangeView(self._start_view_parameters, end_view_parameters)
            c.setCallbackMethod(self._zinc_view.setViewParameters)
            self._undo_redo_stack.push(c)
        else:
            super(Abstract2DHandler, self).mouseReleaseEvent(event)

    def _createSceneviewerFilter(self):
        sceneviewer = self._zinc_view.getSceneviewer()
        scene = sceneviewer.getScene()
        filtermodule = scene.getScenefiltermodule()

        visibility_filter = filtermodule.createScenefilterVisibilityFlags()
        name_filter1 = filtermodule.createScenefilterGraphicsName(IMAGE_PLANE_GRAPHIC_NAME)
        name_filter2 = filtermodule.createScenefilterGraphicsName(POINT_CLOUD_ON_PLANE_GRAPHIC_NAME)
        name_filter3 = filtermodule.createScenefilterGraphicsName(CURVE_ON_PLANE_GRAPHIC_NAME)
        name_filter4 = filtermodule.createScenefilterGraphicsName(SELECTION_BOX_2D_GRAPHIC_NAME)

        name_filter = filtermodule.createScenefilterOperatorOr()
        name_filter.appendOperand(name_filter1)
        name_filter.appendOperand(name_filter2)
        name_filter.appendOperand(name_filter3)
        name_filter.appendOperand(name_filter4)

        master_filter = filtermodule.createScenefilterOperatorAnd()
        master_filter.appendOperand(visibility_filter)
        master_filter.appendOperand(name_filter)

        return master_filter


