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
from PySide import QtCore

from mapclientplugins.segmentationstep.tools.handlers.abstractselection import AbstractSelection
from mapclientplugins.segmentationstep.definitions import ViewMode
from mapclientplugins.segmentationstep.undoredo import CommandNode
from mapclientplugins.segmentationstep.segmentpoint import SegmentPointStatus
from mapclientplugins.segmentationstep.maths.algorithms import calculateLinePlaneIntersection

class Curve(AbstractSelection):

    def __init__(self, plane, undo_redo_stack):
        super(Curve, self).__init__(plane, undo_redo_stack)
        self._mode_type = ViewMode.SEGMENT_CURVE
        self._model = None
        self._scenviewer_filter = None
        self._sceneviewer_filter_orignal = None
        self._streaming_create = False

    def setModel(self, model):
        self._model = model

    def setStreamingCreate(self, state):
        self._streaming_create = state

    def enter(self):
        super(Curve, self).enter()

    def leave(self):
        super(Curve, self).leave()

    def mousePressEvent(self, event):
        self._node_status = None
        if (event.modifiers() & QtCore.Qt.CTRL) and event.button() == QtCore.Qt.LeftButton:
            node = self._zinc_view.getNearestNode(event.x(), event.y())
            if node and node.isValid():
                # node exists at this location so select it
                group = self._model.getSelectionGroup()
                group.removeAllNodes()
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
            super(Curve, self).mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if self._node_status is not None:
            node = self._model.getNodeByIdentifier(self._node_status.getNodeIdentifier())
            point_on_plane = self._calculatePointOnPlane(event.x(), event.y())
            self._model.setNodeLocation(node, point_on_plane)
            if self._streaming_create:
                node_id = -1
                plane_attitude = self._plane.getAttitude()
                fake_status = SegmentPointStatus(node_id, None, None)
                node_status = SegmentPointStatus(node_id, point_on_plane, plane_attitude)
                c = CommandNode(self._model, fake_status, node_status)
                self._undo_redo_stack.push(c)
        else:
            super(Curve, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._node_status is not None:
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
            super(Curve, self).mouseReleaseEvent(event)

    def _calculatePointOnPlane(self, x, y):
        far_plane_point = self._zinc_view.unproject(x, -y, -1.0)
        near_plane_point = self._zinc_view.unproject(x, -y, 1.0)
        point_on_plane = calculateLinePlaneIntersection(near_plane_point, far_plane_point, self._plane.getRotationPoint(), self._plane.getNormal())
        return point_on_plane


