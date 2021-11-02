"""
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
"""
from PySide2 import QtCore

from mapclientplugins.segmentationstep.tools.handlers.abstractselection import AbstractSelection
from mapclientplugins.segmentationstep.definitions import ViewMode
from mapclientplugins.segmentationstep.undoredo import CommandPointCloudNode, CommandMovePlane
from mapclientplugins.segmentationstep.segmentpoint import SegmentPointStatus
from mapclientplugins.segmentationstep.maths.algorithms import calculateLinePlaneIntersection


class Point(AbstractSelection):

    def __init__(self, plane, undo_redo_stack):
        super(Point, self).__init__(plane, undo_redo_stack)
        self._mode_type = ViewMode.SEGMENT_POINT
        self._model = None
        self._streaming_create = False
        self._node_status = None

    def setModel(self, model):
        self._model = model

    def setStreamingCreate(self, state):
        self._streaming_create = state

    def enter(self):
        super(Point, self).enter()

    def leave(self):
        super(Point, self).leave()

    def mousePressEvent(self, event):
        if self._active_button != QtCore.Qt.NoButton:
            return

        self._active_button = event.button()

        self._node_status = None
        self._start_plane_attitude = None
        if (event.modifiers() & QtCore.Qt.CTRL) and event.button() == QtCore.Qt.LeftButton:
            pixel_scale = self._zinc_view.getPixelScale()
            x = event.x() * pixel_scale
            y = event.y() * pixel_scale
            node = self._zinc_view.getNearestNode(x, y)
            if node and node.isValid():
                # node exists at this location so select it
                group = self._model.getSelectionGroup()
                group.removeAllNodes()
                group.addNode(node)

                node_location = self._model.getNodeLocation(node)
                plane_attitude = self._model.getNodePlaneAttitude(node.getIdentifier())
                self._start_plane_attitude = self._plane.getAttitude()
            else:
                node_location = None
                plane_attitude = None
                point_on_plane = self._calculatePointOnPlane(x, y)
                region = self._model.getRegion()
                fieldmodule = region.getFieldmodule()
                fieldmodule.beginChange()
                node = self._model.createNode()
                group = self._model.getPointCloudGroup()
                group.addNode(node)
                self._model.setNodeLocation(node, point_on_plane)
                fieldmodule.endChange()

            self._node_status = SegmentPointStatus(node.getIdentifier(), node_location, plane_attitude)
        else:
            super(Point, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._node_status is not None:
            self._start_plane_attitude = None
            pixel_scale = self._zinc_view.getPixelScale()
            node = self._model.getNodeByIdentifier(self._node_status.getNodeIdentifier())
            point_on_plane = self._calculatePointOnPlane(event.x() * pixel_scale, event.y() * pixel_scale)
            self._model.setNodeLocation(node, point_on_plane)
            if self._streaming_create:
                node_id = -1
                plane_attitude = self._plane.getAttitude()
                fake_status = SegmentPointStatus(node_id, None, None)
                node_status = SegmentPointStatus(node_id, point_on_plane, plane_attitude)
                c = CommandPointCloudNode(self._model, fake_status, node_status)
                self._undo_redo_stack.push(c)
        else:
            super(Point, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._active_button != event.button():
            return

        if self._start_plane_attitude is not None and self._node_status is not None:
            group = self._model.getSelectionGroup()
            group.removeAllNodes()
            target_plane_attitude = self._node_status.getPlaneAttitude()
            if target_plane_attitude != self._start_plane_attitude:
                c = CommandMovePlane(self._plane, self._start_plane_attitude, target_plane_attitude)
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
            c = CommandPointCloudNode(self._model, self._node_status, node_status)
            self._undo_redo_stack.push(c)
        else:
            super(Point, self).mouseReleaseEvent(event)

        self._active_button = QtCore.Qt.NoButton

    def _calculatePointOnPlane(self, x, y):
        far_plane_point = self._zinc_view.unproject(x, -y, -1.0)
        near_plane_point = self._zinc_view.unproject(x, -y, 1.0)
        point_on_plane = calculateLinePlaneIntersection(near_plane_point, far_plane_point, self._plane.getRotationPoint(), self._plane.getNormal())
        return point_on_plane
