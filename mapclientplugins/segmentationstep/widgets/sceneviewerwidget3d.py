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
from mapclientplugins.segmentationstep.widgets.sceneviewerwidget import SceneviewerWidget

class SceneviewerWidget3D(SceneviewerWidget):

    def __init__(self, parent=None, shared=None):
        super(SceneviewerWidget3D, self).__init__(parent, shared)

        self._active_mode = None
        self._modes = {}
        self._plane = None

    def initializeGL(self):
        super(SceneviewerWidget3D, self).initializeGL()

    def _setupUi(self):
        print('Am I actually used')
        self._setGlyphsForGlyphModes(self._rotation_glyph, self._normal_glyph)
        self._setMaterialsForGlyphModes()

    def setModel(self, model):
        self._model = model
        self.setUndoStack(model.getUndoRedoStack())
        self._setupModes(self._model.getImageModel())

    def getPlaneNormalGlyph(self):
        return self._normal_glyph

    def getPlaneRotationGlyph(self):
        return self._rotation_glyph

    def getActiveModeType(self):
        return self._active_mode.getModeType()

    def setActiveModeType(self, mode):
        if (self._active_mode is None or mode != self._active_mode.getModeType()) and mode in self._modes:
            if not self._active_mode is None:
                self._active_mode.leave()
            self._active_mode = self._modes[mode]
            self._active_mode.enter()

    def getMode(self, mode_type='ACTIVE'):
        '''
        Returns the mode specified by mode_type.  If the
        specified mode is not in the _modes dict then it
        returns the currently active mode.
        '''
        if mode_type in self._modes:
            return self._modes[mode_type]

        return self._active_mode

    def addMode(self, mode):
        self._modes[mode.getModeType()] = mode

    def mousePressEvent(self, mouseevent):
        self._active_mode.mousePressEvent(mouseevent)
        if not mouseevent.isAccepted():
            super(SceneviewerWidget3D, self).mousePressEvent(mouseevent)

    def mouseMoveEvent(self, mouseevent):
        self._active_mode.mouseMoveEvent(mouseevent)
        if not mouseevent.isAccepted():
            super(SceneviewerWidget3D, self).mouseMoveEvent(mouseevent)

    def mouseReleaseEvent(self, mouseevent):
        self._active_mode.mouseReleaseEvent(mouseevent)
        if not mouseevent.isAccepted():
            super(SceneviewerWidget3D, self).mouseReleaseEvent(mouseevent)


