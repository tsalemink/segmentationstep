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
        self._field_module = field_module
        self._position = position
        self._updateGL = updateGL
        self._id = -1
        self._node = None

    def redo(self):
        self._field_module.beginChange()
        field_cache = self._field_module.createCache()
        coordinate_field = self._field_module.findFieldByName('coordinates')
        nodeset = self._field_module.findNodesetByName('cmiss_nodes')
        template = nodeset.createNodeTemplate()
        template.defineField(coordinate_field)

        self._node = nodeset.createNode(self._id, template)
        self._id = self._node.getIdentifier()
        field_cache.setNode(self._node)
        coordinate_field.assignReal(field_cache, self._position)

        self._field_module.endChange()

        self._updateGL()

    def undo(self):
        nodeset = self._field_module.findNodesetByName('cmiss_nodes')
        nodeset.destroyNode(self._node)

        self._updateGL()


class CommandMovePlane(QtGui.QUndoCommand):

    def __init__(self, plane_start, plane_end):
        super(CommandMovePlane, self).__init__()
        self._plane_start = plane_start
        self._plane_end = plane_end
        self._set_plane_centre_method = None
        self._set_plane_equation_method = None

    def redo(self):
        self._set_plane_centre_method(self._plane_end.getCentre())
        self._set_plane_equation_method(self._plane_end.getNormal(), self._plane_end.getPoint())

    def undo(self):
        self._set_plane_centre_method(self._plane_start.getCentre())
        self._set_plane_equation_method(self._plane_start.getNormal(), self._plane_start.getPoint())

    def setMethodCallbacks(self, plane_centre, plane_equation):
        self._set_plane_centre_method = plane_centre
        self._set_plane_equation_method = plane_equation


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


