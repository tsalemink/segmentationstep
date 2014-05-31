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

from mapclientplugins.segmentationstep.tools.handlers.planeadjust import PlaneAdjust
from mapclientplugins.segmentationstep.definitions import ViewMode
from mapclientplugins.segmentationstep.maths.vectorops import add, mult, dot, sub
from mapclientplugins.segmentationstep.maths.algorithms import calculateCentroid
from mapclientplugins.segmentationstep.zincutils import getGlyphPosition, setGlyphPosition, createPlaneNormalIndicator
# from mapclientplugins.segmentationstep.tools.resources import images

class Normal(PlaneAdjust):
    '''
    Handle sceneviewer input events when in normal mode.
    The normal mode allows the user to move the plane in 
    the direction of the normal of the plane.  
    '''
    def __init__(self, sceneviewer, plane, undo_redo_stack):
        super(Normal, self).__init__(sceneviewer, plane, undo_redo_stack)
        self._mode_type = ViewMode.PLANE_NORMAL
        self._glyph = createPlaneNormalIndicator(plane.getRegion(), plane.getNormalField())
        self._icon = QtGui.QIcon(':toolbar_icons/normal.png')

    def getIcon(self):
        return self._icon

    def enter(self):
        scene = self._glyph.getScene()
        scene.beginChange()
        super(Normal, self).enter()
        setGlyphPosition(self._glyph, calculateCentroid(self._plane.getRotationPoint(), self._plane.getNormal(), self._get_dimension_method()))
        scene.endChange()

    def mouseMoveEvent(self, event):
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            pos = getGlyphPosition(self._glyph)
            screen_pos = self._view.project(pos[0], pos[1], pos[2])
            global_cur_pos = self._view.unproject(event.x(), -event.y(), screen_pos[2])
            global_old_pos = self._view.unproject(self._previous_mouse_position[0], -self._previous_mouse_position[1], screen_pos[2])
            global_pos_diff = sub(global_cur_pos, global_old_pos)

            n = self._plane.getNormal()
            proj_n = mult(n, dot(global_pos_diff, n))
            new_pos = add(pos, proj_n)
            scene = self._glyph.getScene()
            scene.beginChange()

            plane_centre = calculateCentroid(new_pos, self._plane.getNormal(), self._get_dimension_method())
            if plane_centre is not None:
                self._plane.setRotationPoint(plane_centre)
                setGlyphPosition(self._glyph, plane_centre)

            scene.endChange()
            self._previous_mouse_position = [event.x(), event.y()]
        else:
            super(Normal, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        scene = self._glyph.getScene()
        scene.beginChange()
        set_undo_redo_command = False
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            point_on_plane = getGlyphPosition(self._glyph)
            self._plane.setRotationPoint(point_on_plane)
            set_undo_redo_command = True

        super(Normal, self).mouseReleaseEvent(event)
        scene.endChange()

        if set_undo_redo_command:
            self.setUndoRedoCommand('plane normal')


