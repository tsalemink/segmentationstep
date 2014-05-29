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
from mapclientplugins.segmentationstep.tools.abstracttool import AbstractTool
from mapclientplugins.segmentationstep.undoredo import CommandMovePlane, CommandMoveGlyph
from mapclientplugins.segmentationstep.zincutils import setGlyphPosition
from mapclientplugins.segmentationstep.plane import PlaneAttitude

class PlaneAdjust(AbstractTool):

    def __init__(self, sceneviewer, plane, undo_redo_stack):
        super(PlaneAdjust, self).__init__(sceneviewer, plane, undo_redo_stack)
        self._glyph = None
        self._glyph_picker_method = None
        self._plane_attitude_start = None
        self._plane_attitude_end = None
        self._default_material = None
        self._selected_material = None

    def setGlyph(self, glyph):
        self._glyph = glyph

    def getGlyph(self):
        return self._glyph

    def setDefaultMaterial(self, material):
        self._default_material = material

    def setSelectedMaterial(self, material):
        self._selected_material = material

    def enter(self):
        self._glyph.setVisibilityFlag(True)
        self._glyph.setMaterial(self._default_material)

    def leave(self):
        self._glyph.setVisibilityFlag(False)

    def setUndoRedoCommand(self, name):
        if self._plane_attitude_start != self._plane_attitude_end:
            self._undo_redo_stack.beginMacro(name)

            c1 = CommandMovePlane(self._plane, self._plane_attitude_start, self._plane_attitude_end)
            self._undo_redo_stack.push(c1)
            c2 = CommandMoveGlyph(self._glyph, self._plane_attitude_start.getPoint(), self._plane_attitude_end.getPoint())
            c2.setGlyphMoveMethod(setGlyphPosition)
            self._undo_redo_stack.push(c2)

            self._undo_redo_stack.endMacro()

    def mousePressEvent(self, event):
        super(PlaneAdjust, self).mousePressEvent(event)
        self._previous_mouse_position = [event.x(), event.y()]
        self._plane_attitude_start = PlaneAttitude(self._plane.getRotationPoint(), self._plane.getNormal())
        graphic = self._view.getNearestGraphicsPoint(event.x(), event.y())
        if graphic and graphic.isValid():
            graphic.setMaterial(self._selected_material)

    def mouseReleaseEvent(self, event):
        super(PlaneAdjust, self).mouseReleaseEvent(event)
        self._plane_attitude_end = PlaneAttitude(self._plane.getRotationPoint(), self._plane.getNormal())
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            self._glyph.setMaterial(self._default_material)
