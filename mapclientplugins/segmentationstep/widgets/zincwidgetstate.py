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
from mapclientplugins.segmentationstep.widgets.zincwidget import ZincWidget
from mapclientplugins.segmentationstep.maths.vectorops import add

class ZincWidgetState(ZincWidget):

    def __init__(self, parent=None, shared=None):
        super(ZincWidgetState, self).__init__(parent, shared)

        self._active_mode = None
        self._modes = {}

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

    def viewAll(self):
        self._active_mode.viewAll()

    def mousePressEvent(self, event):
        self._active_mode.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self._active_mode.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._active_mode.mouseReleaseEvent(event)

    def setPlane(self, plane):
        self._plane = plane
        self._plane.notifyChange.addObserver(self.setViewToPlane)

    def setViewToPlane(self):
        normal = self._plane.getNormal()
        centre = self._plane.getRotationPoint()
        _, _, up, angle = self.getViewParameters()
        self.setViewParameters(add(normal, centre), centre, up, angle)
        self.viewAll()


