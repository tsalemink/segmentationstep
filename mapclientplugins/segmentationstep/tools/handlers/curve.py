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

from mapclientplugins.segmentationstep.tools.handlers.abstracthandler import AbstractHandler
from mapclientplugins.segmentationstep.definitions import ViewMode
from mapclientplugins.segmentationstep.zincutils import setGlyphSize, setGlyphOffset, COORDINATE_SYSTEM_LOCAL
from mapclientplugins.segmentationstep.undoredo import CommandNode, CommandSelection
from mapclientplugins.segmentationstep.segmentpoint import SegmentPointStatus
from mapclientplugins.segmentationstep.maths.algorithms import calculateLinePlaneIntersection

class SelectionMode(object):

    NONE = -1
    EXCULSIVE = 0
    ADDITIVE = 1

class Spline(AbstractHandler):

    def __init__(self, plane, undo_redo_stack):
        super(Spline, self).__init__(plane, undo_redo_stack)
        self._mode_type = ViewMode.SEGMENT_POINT
        self._model = None
        self._selection_box = None
        self._selection_mode = SelectionMode.NONE
        self._selection_position_start = None
        self._scenviewer_filter = None
        self._sceneviewer_filter_orignal = None
        self._streaming_create = False

    def setModel(self, model):
        self._model = model

    def setStreamingCreate(self, state):
        self._streaming_create = state

    def enter(self):
        super(Spline, self).enter()

    def leave(self):
        super(Spline, self).leave()

    def mousePressEvent(self, event):
        self._selection_mode = SelectionMode.NONE
        self._node_status = None
        if event.modifiers() & QtCore.Qt.SHIFT and event.button() == QtCore.Qt.LeftButton:
            self._selection_position_start = [event.x(), event.y()]
            self._selection_mode = SelectionMode.EXCULSIVE
            if event.modifiers() & QtCore.Qt.ALT:
                self._selection_mode = SelectionMode.ADDITIVE

            self._start_selection = self._model.getCurrentSelection()
        elif (event.modifiers() & QtCore.Qt.CTRL) and event.button() == QtCore.Qt.LeftButton:
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
            super(Spline, self).mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if self._selection_mode != SelectionMode.NONE:
            x = event.x()
            y = event.y()
            xdiff = float(x - self._selection_position_start[0])
            ydiff = float(y - self._selection_position_start[1])
            if abs(xdiff) < 0.0001:
                xdiff = 1
            if abs(ydiff) < 0.0001:
                ydiff = 1
            xoff = float(self._selection_position_start[0]) / xdiff + 0.5
            yoff = float(self._selection_position_start[1]) / ydiff + 0.5
            scene = self._selection_box.getScene()
            scene.beginChange()
            setGlyphSize(self._selection_box, [xdiff, -ydiff, 0.999])
            setGlyphOffset(self._selection_box, [xoff, yoff, 0])
            self._selection_box.setVisibilityFlag(True)
            scene.endChange()
        elif self._node_status is not None:
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
            super(Spline, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._selection_mode != SelectionMode.NONE:
            x = event.x()
            y = event.y()
            # Construct a small frustrum to look for nodes in.
            region = self._model.getRegion()
            region.beginHierarchicalChange()
            self._selection_box.setVisibilityFlag(False)
            selection_group = self._model.getSelectionGroupField()

            if (x != self._selection_position_start[0] and y != self._selection_position_start[1]):
                left = min(x, self._selection_position_start[0])
                right = max(x, self._selection_position_start[0])
                bottom = min(y, self._selection_position_start[1])
                top = max(y, self._selection_position_start[1])
                self._zinc_view.setPickingRectangle(COORDINATE_SYSTEM_LOCAL, left, bottom, right, top)
                if self._selection_mode == SelectionMode.EXCULSIVE:
                    selection_group.clear()
                self._zinc_view.addPickedNodesToFieldGroup(selection_group)
            else:
                node = self._zinc_view.getNearestNode(x, y)
                if self._selection_mode == SelectionMode.EXCULSIVE and not node.isValid():
                    selection_group.clear()

                if node.isValid():
                    group = self._model.getSelectionGroup()
                    if self._selection_mode == SelectionMode.EXCULSIVE:
                        remove_current = group.getSize() == 1 and group.containsNode(node)
                        selection_group.clear()
                        if not remove_current:
                            group.addNode(node)
                    elif self._selection_mode == SelectionMode.ADDITIVE:
                        if group.containsNode(node):
                            group.removeNode(node)
                        else:
                            group.addNode(node)

            end_selection = self._model.getCurrentSelection()
            c = CommandSelection(self._model, self._start_selection, end_selection)
            self._undo_redo_stack.push(c)
            region.endHierarchicalChange()
            self._selection_mode = SelectionMode.NONE
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
            super(Spline, self).mouseReleaseEvent(event)

    def _calculatePointOnPlane(self, x, y):
        far_plane_point = self._zinc_view.unproject(x, -y, -1.0)
        near_plane_point = self._zinc_view.unproject(x, -y, 1.0)
        point_on_plane = calculateLinePlaneIntersection(near_plane_point, far_plane_point, self._plane.getRotationPoint(), self._plane.getNormal())
        return point_on_plane


