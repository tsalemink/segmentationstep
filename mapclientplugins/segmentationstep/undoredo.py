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
from PySide import QtGui

from mapclientplugins.segmentationstep.plane import PlaneAttitude
from mapclientplugins.segmentationstep.maths.vectorops import mult, add
from mapclientplugins.segmentationstep.model.curve import CurveModel

class CommandMovePlane(QtGui.QUndoCommand):

    def __init__(self, plane, plane_start, plane_end):
        super(CommandMovePlane, self).__init__()
        self.setText('Move Plane')
        self._plane_start = plane_start
        self._plane_end = plane_end
        self._plane = plane

    def redo(self):
        self._plane.setPlaneEquation(self._plane_end.getNormal(), self._plane_end.getPoint())

    def undo(self):
        self._plane.setPlaneEquation(self._plane_start.getNormal(), self._plane_start.getPoint())

class CommandMoveGlyph(QtGui.QUndoCommand):

    def __init__(self, glyph, start_location, end_location):
        super(CommandMoveGlyph, self).__init__()
        self.setText('Move Glyph')
        self._start_location = start_location
        self._end_location = end_location
        self._glyph = glyph
        self._glyph_move_method = None

    def setGlyphMoveMethod(self, glyph_move_method):
        self._glyph_move_method = glyph_move_method

    def redo(self):
        self._glyph_move_method(self._glyph, self._end_location)

    def undo(self):
        self._glyph_move_method(self._glyph, self._start_location)


class CommandChangeView(QtGui.QUndoCommand):

    def __init__(self, view_start, view_end):
        super(CommandChangeView, self).__init__()
        self.setText('Change View')
        self._view_start = view_start
        self._view_end = view_end
        self._set_viewport_parameters_method = None

    def redo(self):
        self._set_viewport_parameters_method(self._view_end[0], self._view_end[1],
                                             self._view_end[2], self._view_end[3])

    def undo(self):
        self._set_viewport_parameters_method(self._view_start[0], self._view_start[1],
                                             self._view_start[2], self._view_start[3])

    def setCallbackMethod(self, viewport_parameters):
        self._set_viewport_parameters_method = viewport_parameters


class CommandChangeViewHandler(QtGui.QUndoCommand):

    def __init__(self, current_handler, current_action, new_handler, new_action):
        super(CommandChangeViewHandler, self).__init__()
        self.setText('Change View Handler')
        self._current_handler = current_handler
        self._current_action = current_action
        self._new_handler = new_handler
        self._new_action = new_action
        self._set_active_mode_type_method = None

    def setSetChangeHandlerMethod(self, method):
        self._set_change_handler_method = method

    def _setActionState(self, new):
        self._new_action.blockSignals(True)
        self._new_action.setChecked(new)
        self._new_action.blockSignals(False)
        self._current_action.blockSignals(True)
        self._current_action.setChecked(not new)
        self._current_action.blockSignals(False)

    def redo(self):
        self._setActionState(True)
        self._set_change_handler_method(self._new_handler)

    def undo(self):
        self._setActionState(False)
        self._set_change_handler_method(self._current_handler)


class CommandCurrentNew(QtGui.QUndoCommand):

    def __init__(self, current, new):
        super(CommandCurrentNew, self).__init__()
        self._current = current
        self._new = new


class CommandSetScale(CommandCurrentNew):

    def __init__(self, current, new, scale_index):
        super(CommandSetScale, self).__init__(current, new)
        self.setText('Set Scale')
        self._scale_index = scale_index
        self._set_scale_method = None
        self._line_edit = None

    def setLineEdit(self, line_edit):
        self._line_edit = line_edit

    def setSetScaleMethod(self, method):
        self._set_scale_method = method

    def redo(self):
        self._set_scale_method(self._new)
        self._line_edit.setText(str(self._new[self._scale_index]))

    def undo(self):
        self._set_scale_method(self._current)
        self._line_edit.setText(str(self._current[self._scale_index]))


class CommandSetSingleParameterMethod(CommandCurrentNew):

    def __init__(self, current, new):
        super(CommandSetSingleParameterMethod, self).__init__(current, new)
        self.setText('Single Parameter')

        self._set_single_parameter_method = None

    def setSingleParameterMethod(self, method):
        self._set_single_parameter_method = method

    def redo(self):
        self._set_single_parameter_method(self._new)

    def undo(self):
        self._set_single_parameter_method(self._current)


class CommandSetGraphicVisibility(CommandCurrentNew):

    def __init__(self, current, new):
        super(CommandSetGraphicVisibility, self).__init__(current, new)
        self.setText('Graphic Visibility')
        self._graphic = None
        self._check_box = None

    def setGraphic(self, graphic):
        self._graphic = graphic

    def setCheckBox(self, check_box):
        self._check_box = check_box

    def redo(self):
        self._graphic.setVisibilityFlag(self._new)
        self._check_box.setChecked(self._new)

    def undo(self):
        self._graphic.setVisibilityFlag(self._current)
        self._check_box.setChecked(self._current)


class CommandSetGlyphSize(CommandCurrentNew):

    def __init__(self, current, new, glyph):
        super(CommandSetGlyphSize, self).__init__(current, new)
        self.setText('Graphic Size')
        self._set_glyph_size_method = None
        self._spin_box = None
        self._glyph = glyph if type(glyph) is list else [glyph]

    def setSpinBox(self, spin_box):
        self._spin_box = spin_box

    def setSetGlyphSizeMethod(self, method):
        self._set_glyph_size_method = method

    def redo(self):
        for glyph in self._glyph:
            self._set_glyph_size_method(glyph, self._new)
        self._spin_box.setValue(self._new[0])

    def undo(self):
        for glyph in self._glyph:
            self._set_glyph_size_method(glyph, self._current)
        self._spin_box.setValue(self._current[0])


class CommandNode(QtGui.QUndoCommand):

    def __init__(self, node_model, node_status_start, node_status_end):
        super(CommandNode, self).__init__()
        self.setText('Node')
        self._model = node_model
        self._status_start = node_status_start
        self._status_end = node_status_end

    def _setNodeIdentifier(self, node_id):
        self._status_start.setNodeIdentifier(node_id)
        self._status_end.setNodeIdentifier(node_id)

    def _removeNode(self, node_id):
        self._model.removeNode(node_id)
        self._setNodeIdentifier(-1)

    def _addNode(self, node_id, location, plane_attitude):
        node_id = self._model.addNode(node_id, location, plane_attitude)
        self._addNodeToGroup(node_id)
        self._setNodeIdentifier(node_id)

        return node_id


class CommandPointCloudNode(CommandNode):

    def _addNodeToGroup(self, node_id):
        node = self._model.getNodeByIdentifier(node_id)
        group = self._model.getPointCloudGroup()
        group.addNode(node)

    def redo(self):
        node_id = self._status_end.getNodeIdentifier()
        location = self._status_end.getLocation()
        plane_attitude = self._status_end.getPlaneAttitude()
        if location is None:
            self._removeNode(node_id)
        else:
            previous_location = self._status_start.getLocation()
            if previous_location is None:
                self._addNode(node_id, location, plane_attitude)
            else:
                self._model.modifyNode(node_id, location, plane_attitude)

    def undo(self):
        node_id = self._status_start.getNodeIdentifier()
        location = self._status_start.getLocation()
        plane_attitude = self._status_start.getPlaneAttitude()
        if location is None:
            self._removeNode(node_id)
        else:
            next_location = self._status_end.getLocation()
            if next_location is None:
                self._addNode(node_id, location, plane_attitude)
            else:
                self._model.modifyNode(node_id, location, plane_attitude)


class CommandCurveNode(CommandNode):

    def setScene(self, scene):
        self._scene = scene

    def _addNodeToGroup(self, node_id):
        node = self._model.getNodeByIdentifier(node_id)
        group = self._model.getCurveGroup()
        group.addNode(node)

    def _updateInterpolationPoints(self, curve):
        curve_index = self._model.getCurveIndex(curve)
        if len(curve) > 1:
            locations = curve.calculate()
            self._scene.setInterpolationPoints(curve_index, locations)
        else:
            self._scene.clearInterpolationPoints(curve_index)

    def redo(self):
        node_id = self._status_end.getNodeIdentifier()
        location = self._status_end.getLocation()
        plane_attitude = self._status_end.getPlaneAttitude()
        curve_index = self._status_end.getCurveIndex()
        curve = self._model.getCurveAtIndex(curve_index)
        if location is None:
            curve.removeNode(node_id)
            if not curve.closes(node_id):
                self._removeNode(node_id)
            self._updateInterpolationPoints(curve)
        else:
            previous_location = self._status_start.getLocation()
            if previous_location is None:
                if not curve.closes(node_id):
                    node_id = self._addNode(node_id, location, plane_attitude)
                curve.addNode(node_id)
                self._updateInterpolationPoints(curve)
            else:
                self._model.modifyNode(node_id, location, plane_attitude)
                self._updateInterpolationPoints(curve)

    def undo(self):
        node_id = self._status_start.getNodeIdentifier()
        location = self._status_start.getLocation()
        plane_attitude = self._status_start.getPlaneAttitude()
        curve_index = self._status_end.getCurveIndex()
        curve = self._model.getCurveAtIndex(curve_index)
        if location is None:
            curve.removeNode(node_id)
            if not curve.closes(node_id):
                self._removeNode(node_id)
            self._updateInterpolationPoints(curve)
        else:
            next_location = self._status_end.getLocation()
            if next_location is None:
                if not curve.closes(node_id):
                    node_id = self._addNode(node_id, location, plane_attitude)
                curve.addNode(node_id)
                self._updateInterpolationPoints(curve)
            else:
                self._model.modifyNode(node_id, location, plane_attitude)
                self._updateInterpolationPoints(curve)


class CommandSelection(QtGui.QUndoCommand):

    def __init__(self, model, selection_start, selection_end):
        super(CommandSelection, self).__init__()
        self.setText('Selection')
        self._model = model
        self._selection_start = selection_start
        self._selection_end = selection_end

    def redo(self):
        self._model.setSelection(self._selection_end)

    def undo(self):
        self._model.setSelection(self._selection_start)


class CommandDelete(QtGui.QUndoCommand):

    def __init__(self, model, selected):
        super(CommandDelete, self).__init__()
        self.setText('Delete')
        self._model = model
        self._node_statuses = []
        for node_id in selected:
            self._node_statuses.append(model.getNodeStatus(node_id))

    def redo(self):
        region = self._model.getRegion()
        scene = region.getScene()

        scene.beginChange()
        self._model.removeNodes(self._node_statuses)

        scene.endChange()

    def undo(self):
        region = self._model.getRegion()
        scene = region.getScene()
        scene.beginChange()

        node_ids = self._model.createNodes(self._node_statuses, group=self._model.getPointCloudGroup())
        self._model.setSelection(node_ids)

        scene.endChange()


class CommandDeleteCurve(QtGui.QUndoCommand):

    def __init__(self, model, selected):
        super(CommandDeleteCurve, self).__init__()
        self.setText('Delete')
        self._model = model
        self._node_statuses = {}
        self._curves = {}
        self._interpolation_counts = {}
        self._selected = selected
        self._scene = None
        different_curves = []
        for node_id in selected:
            curve = self._model.getCurveForNode(node_id)
            curve_identifier = self._model.getCurveIndex(curve)
            if curve_identifier not in different_curves:
                different_curves.append(curve_identifier)
                self._curves[curve_identifier] = curve
                self._interpolation_counts[curve_identifier] = curve.getInterpolationCount()
                self._node_statuses[curve_identifier] = []
                for node_id in curve.getNodes():
                    self._node_statuses[curve_identifier].append(model.getNodeStatus(node_id))

    def setScene(self, scene):
        self._scene = scene

    def redo(self):
        region = self._model.getRegion()
        scene = region.getScene()
        scene.beginChange()

        for curve_identifier in self._curves:
            self._scene.clearInterpolationPoints(curve_identifier)
            self._model.popCurve(curve_identifier)
            self._curves[curve_identifier] = None

        scene.endChange()

    def undo(self):
        region = self._model.getRegion()
        scene = region.getScene()
        scene.beginChange()

        node_ids = []
        for curve_identifier in self._curves:
            if self._curves[curve_identifier] is None:
                curve = CurveModel(self._model)
                self._model.insertCurve(curve_identifier, curve)
                curve.setInterpolationCount(self._interpolation_counts[curve_identifier])
                node_ids = self._model.createNodes(self._node_statuses[curve_identifier], group=self._model.getCurveGroup())
                curve.setNodes(node_ids)
                self._curves[curve_identifier] = curve
                if len(curve) > 1:
                    locations = curve.calculate()
                    self._scene.setInterpolationPoints(curve_identifier, locations)

        self._model.setSelection(self._selected)

        scene.endChange()

class AbstractCommandPushPull(QtGui.QUndoCommand):

    def __init__(self, model, selected, scale):
        super(AbstractCommandPushPull, self).__init__()
        self.setText('Push/Pull')
        self._rotation_point_start = None
        self._rotation_point_end = None
        self._normal = None
        self._model = model
        self._selected = selected
        self._node_statuses = self._adjustNodeLocation(selected, scale)
        self._set_rotation_point_method = None
        self._set_normal_method = None

    def setSetRotationPointMethod(self, set_rotation_point_method):
        self._set_rotation_point_method = set_rotation_point_method

    def setSetNormalMethod(self, set_normal_method):
        self._set_normal_method = set_normal_method

    def _adjustNodeLocation(self, selected, scale):
        '''
        Adjust the node location by adding the scaled normal
        for the plane.
        '''
        node_statuses = []
        for node_id in selected:
            node_status = self._model.getNodeStatus(node_id)
            location = node_status.getLocation()
            plane_attitude = node_status.getPlaneAttitude()
            normal = plane_attitude.getNormal()
            point_on_plane = plane_attitude.getPoint()
            if self._rotation_point_start is None:
                self._normal = normal
                self._rotation_point_start = point_on_plane
            adjustment = mult(normal, scale)

            point_on_plane = add(point_on_plane, adjustment)
            if self._rotation_point_end is None:
                self._rotation_point_end = point_on_plane
            plane_attitude = PlaneAttitude(point_on_plane, normal)
            node_status.setLocation(add(location, adjustment))
            node_status.setPlaneAttitude(plane_attitude)

            node_statuses.append(node_status)

        return node_statuses

def _updateNodeIdentifiers(node_statuses, node_ids):
    for i, node_status in enumerate(node_statuses):
        node_status.setNodeIdentifier(node_ids[i])


class CommandPushPull(AbstractCommandPushPull):

    def redo(self):
        region = self._model.getRegion()
        scene = region.getScene()
        scene.beginChange()

        node_ids = self._model.createNodes(self._node_statuses, group=self._model.getPointCloudGroup())
        self._model.setSelection(node_ids)
        _updateNodeIdentifiers(self._node_statuses, node_ids)
        self._set_rotation_point_method(self._rotation_point_end)
        self._set_normal_method(self._normal)

        scene.endChange()

    def undo(self):
        region = self._model.getRegion()
        scene = region.getScene()
        scene.beginChange()

        self._model.removeNodes(self._node_statuses)
        self._model.setSelection(self._selected)
        self._set_rotation_point_method(self._rotation_point_start)
        self._set_normal_method(self._normal)

        scene.endChange()


class CommandPushPullCurve(AbstractCommandPushPull):

    def __init__(self, model, selected, scale):
        super(CommandPushPullCurve, self).__init__(model, selected, scale)
        self._scene = None
        self._node_statuses = {}
        self._curves = {}
        self._interpolation_counts = {}
        different_curves = []
        for node_id in selected:
            curve = self._model.getCurveForNode(node_id)
            curve_identifier = self._model.getCurveIndex(curve)
            if curve_identifier not in different_curves:
                different_curves.append(curve_identifier)
                self._curves[curve_identifier] = curve_identifier
                self._interpolation_counts[curve_identifier] = curve.getInterpolationCount()
                self._node_statuses[curve_identifier] = self._adjustNodeLocation(curve.getNodes(), scale)

    def setScene(self, scene):
        self._scene = scene

    def redo(self):
        region = self._model.getRegion()
        scene = region.getScene()
        scene.beginChange()

        selection_node_ids = []
        for curve_identifier in self._curves:
            node_statuses = self._node_statuses[curve_identifier]
            node_ids = self._model.createNodes(node_statuses, group=self._model.getCurveGroup())
            _updateNodeIdentifiers(node_statuses, node_ids)
            curve = CurveModel(self._model)
            curve_count = self._model.getCurveCount()
            self._model.insertCurve(curve_count, curve)
            curve.setInterpolationCount(self._interpolation_counts[curve_identifier])
            curve.setNodes(node_ids)
            self._curves[curve_identifier] = curve_count
            if len(curve) > 1:
                locations = curve.calculate()
                self._scene.setInterpolationPoints(curve_count, locations)
            selection_node_ids += node_ids

        self._model.setSelection(selection_node_ids)
        self._set_rotation_point_method(self._rotation_point_end)
        self._set_normal_method(self._normal)

        scene.endChange()

    def undo(self):
        region = self._model.getRegion()
        scene = region.getScene()
        scene.beginChange()

        for old_curve_identifier in self._curves:
            new_curve_identifier = self._curves[old_curve_identifier]
            self._scene.clearInterpolationPoints(new_curve_identifier)
            self._model.popCurve(new_curve_identifier)

        self._model.setSelection(self._selected)
        self._set_rotation_point_method(self._rotation_point_start)
        self._set_normal_method(self._normal)

        scene.endChange()


