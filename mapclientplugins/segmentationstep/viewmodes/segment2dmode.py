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

from mapclientplugins.segmentationstep.viewmodes.segmentmode import SegmentMode
from mapclientplugins.segmentationstep.maths.vectorops import add, mult, cross, dot, sub, normalize, magnitude
from mapclientplugins.segmentationstep.maths.algorithms import calculateCentroid, calculateLinePlaneIntersection
from mapclientplugins.segmentationstep.undoredo import CommandChangeView, CommandNode
from mapclientplugins.segmentationstep.segmentpoint import SegmentPointStatus

class SegmentMode2D(SegmentMode):

    def __init__(self, sceneviewer, plane, undo_redo_stack):
        super(SegmentMode2D, self).__init__(sceneviewer, plane, undo_redo_stack)
        self._start_position = None
        self._model = None

    def setModel(self, model):
        self._model = model

    def mousePressEvent(self, event):
        self._node = None
        self._start_position = None
        self._node_status = None
        if not event.modifiers() and event.button() == QtCore.Qt.LeftButton:
            self._start_position = [event.x(), event.y()]
            self._start_view_parameters = self._view.getViewParameters()
        elif (event.modifiers() & QtCore.Qt.CTRL) and event.button() == QtCore.Qt.LeftButton:
            node = self._view.getNearestNode(event.x(), event.y())
            if node and node.isValid():
                # node exists at this location so select it
                group = self._model.getSelectionGroup()
                group.removeAllNodes()
#                 node = None
                group.addNode(node)
                node_location = self._model.getNodeLocation(node)
                plane_attitude = self._model.getNodePlaneAttitude(node.getIdentifier())
            else:
                node_location = None
                plane_attitude = None
                point_on_plane = self._calculatePointOnPlane(event.x(), event.y())
                region = self._model.getRegion()
                fieldmodule = region.getFieldmodule()
                fieldmodule.beginChange()
                node = self._model.createNode()
                self._model.setNodeLocation(node, point_on_plane)
                fieldmodule.endChange()

            self._node_status = SegmentPointStatus(node.getIdentifier(), node_location, plane_attitude)
        else:
            super(SegmentMode2D, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._start_position is not None:
            # v_rot = v*cos(theta)+(wxv)*sin(theta)+w*(w.v)*(1-cos(theta))
            # v is our vector
            # w is the unit vector to rotate around
            # theta is the angle to rotate
            if self._start_position[0] == event.x() and self._start_position[1] == event.y():
                return
            centre_point = calculateCentroid(self._plane.getRotationPoint(), self._plane.getNormal(), self._get_dimension_method())
            centre_widget = self._view.project(centre_point[0], centre_point[1], centre_point[2])
            a = sub(centre_widget, [event.x(), -event.y(), centre_widget[2]])
            b = sub(centre_widget, [self._start_position[0], -self._start_position[1], centre_widget[2]])
            c = dot(a, b)
            d = magnitude(a) * magnitude(b)
            theta = acos(min(c / d, 1.0))
            if theta != 0.0:
                g = cross(a, b)
                lookat, eye, up, angle = self._view.getViewParameters()
                w = normalize(sub(lookat, eye))
                if copysign(1, dot(g, [0, 0, 1])) < 0:
                    theta = -theta
                v = up
                p1 = mult(v, cos(theta))
                p2 = mult(cross(w, v), sin(theta))
                p3a = mult(w, dot(w, v))
                p3 = mult(p3a, 1 - cos(theta))
                v_rot = add(p1, add(p2, p3))
                self._view.setViewParameters(lookat, eye, v_rot, angle)
                self._start_position = [event.x(), event.y()]
        elif self._node_status is not None:
            node = self._model.getNodeByIdentifier(self._node_status.getNodeIdentifier())
            point_on_plane = self._calculatePointOnPlane(event.x(), event.y())
            self._model.setNodeLocation(node, point_on_plane)
        else:
            super(SegmentMode2D, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._start_position is not None:
            # Do undo redo command
            end_view_parameters = self._view.getViewParameters()
            c = CommandChangeView(self._start_view_parameters, end_view_parameters)
            c.setCallbackMethod(self._view.setViewParameters)
            self._undo_redo_stack.push(c)
        elif self._node_status is not None:
            # do undo redo command for adding a node or moving a node
            node_id = self._node_status.getNodeIdentifier()
            node = self._model.getNodeByIdentifier(node_id)
            group = self._model.getSelectionGroup()
            group.removeNode(node)
            node_location = self._model.getNodeLocation(node)
            plane_attitude = self._plane.getAttitude()
            node_status = SegmentPointStatus(node_id, node_location, plane_attitude)
            c = CommandNode(self._model, self._node_status, node_status)
            self._undo_redo_stack.push(c)
        else:
            super(SegmentMode2D, self).mouseReleaseEvent(event)

    def _calculatePointOnPlane(self, x, y):
        far_plane_point = self._view.unproject(x, -y, -1.0)
        near_plane_point = self._view.unproject(x, -y, 1.0)
        point_on_plane = calculateLinePlaneIntersection(near_plane_point, far_plane_point, self._plane.getRotationPoint(), self._plane.getNormal())
        return point_on_plane


