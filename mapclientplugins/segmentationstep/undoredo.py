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

class CommandAdd(QtGui.QUndoCommand):
    '''
    '''

    def __init__(self, field_module, position, updateGL):
        super(CommandAdd, self).__init__()
        self._fieldmodule = field_module
        self._position = position
        self._updateGL = updateGL
        self._id = -1
        self._node = None

    def redo(self):
        self._fieldmodule.beginChange()
        field_cache = self._fieldmodule.createCache()
        coordinate_field = self._fieldmodule.findFieldByName('coordinates')
        nodeset = self._fieldmodule.findNodesetByName('cmiss_nodes')
        template = nodeset.createNodeTemplate()
        template.defineField(coordinate_field)

        self._node = nodeset.createNode(self._id, template)
        self._id = self._node.getIdentifier()
        field_cache.setNode(self._node)
        coordinate_field.assignReal(field_cache, self._position)

        self._fieldmodule.endChange()

        self._updateGL()

    def undo(self):
        nodeset = self._fieldmodule.findNodesetByName('cmiss_nodes')
        nodeset.destroyNode(self._node)

        self._updateGL()


class CommandMovePlane(QtGui.QUndoCommand):

    def __init__(self, plane, plane_start, plane_end):
        super(CommandMovePlane, self).__init__()
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
        self._view_start = view_start
        self._view_end = view_end
        self._set_viewport_parameters_method = None

    def redo(self):
        self._set_viewport_parameters_method(self._view_end.getEye(), self._view_end.getLookat(), self._view_end.getUp())

    def undo(self):
        self._set_viewport_parameters_method(self._view_start.getEye(), self._view_start.getLookat(), self._view_start.getUp())

    def setCallbackMethod(self, viewport_parameters):
        self._set_viewport_parameters_method = viewport_parameters


class CommandAddNode(QtGui.QUndoCommand):

    def __init__(self, fieldmodule, position):
        super(CommandAddNode, self).__init__()
        self._fieldmodule = fieldmodule
        self._nodeset = self._fieldmodule.findNodesetByName('nodes')
        self._coordinate_field = self._fieldmodule.findFieldByName('coordinates')
        self._position = position
        self._id = -1
        self._node = None

    def redo(self):
        self._fieldmodule.beginChange()
        field_cache = self._fieldmodule.createFieldcache()
        template = self._nodeset.createNodetemplate()
        template.defineField(self._coordinate_field)

        self._node = self._nodeset.createNode(self._id, template)
        self._id = self._node.getIdentifier()
        field_cache.setNode(self._node)
        self._coordinate_field.assignReal(field_cache, self._position)

        self._fieldmodule.endChange()

    def undo(self):
        self._nodeset.destroyNode(self._node)


class CommandCurrentNew(QtGui.QUndoCommand):

    def __init__(self, current, new):
        super(CommandCurrentNew, self).__init__()
        self._current = current
        self._new = new


class CommandChangeViewMode(CommandCurrentNew):

    def __init__(self, current, new):
        super(CommandChangeViewMode, self).__init__(current, new)
        self._set_active_mode_type_method = None
        self._set_view_mode_ui_method = None

    def setSetActiveModeTypeMethod(self, method):
        self._set_active_mode_type_method = method

    def setSetViewModeUiMethod(self, method):
        self._set_view_mode_ui_method = method

    def redo(self):
        self._set_active_mode_type_method(self._new)
        self._set_view_mode_ui_method(self._new)

    def undo(self):
        self._set_active_mode_type_method(self._current)
        self._set_view_mode_ui_method(self._current)


class CommandSetScale(CommandCurrentNew):

    def __init__(self, current, new, scale_index):
        super(CommandSetScale, self).__init__(current, new)
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


class CommandSetProjectionMode(CommandCurrentNew):

    def __init__(self, current, new):
        super(CommandSetProjectionMode, self).__init__(current, new)
        self._set_projection_mode_method = None

    def setSetProjectionModeMethod(self, method):
        self._set_projection_mode_method = method

    def redo(self):
        self._set_projection_mode_method(self._new)

    def undo(self):
        self._set_projection_mode_method(self._current)


class CommandSetGraphicVisibility(CommandCurrentNew):

    def __init__(self, current, new):
        super(CommandSetGraphicVisibility, self).__init__(current, new)
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
        self._set_glyph_size_method = None
        self._spin_box = None
        self._glyph = glyph

    def setSpinBox(self, spin_box):
        self._spin_box = spin_box

    def setSetGlyphSizeMethod(self, method):
        self._set_glyph_size_method = method

    def redo(self):
        self._set_glyph_size_method(self._glyph, self._new)
        self._spin_box.setValue(self._new[0])

    def undo(self):
        self._set_glyph_size_method(self._glyph, self._current)
        self._spin_box.setValue(self._current[0])


