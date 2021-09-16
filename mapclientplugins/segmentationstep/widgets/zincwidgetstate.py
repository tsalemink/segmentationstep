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
from mapclientplugins.segmentationstep.widgets.zincwidget import ZincWidget
from mapclientplugins.segmentationstep.maths.vectorops import add, sub, \
    magnitude, mult


class ZincWidgetState(ZincWidget):

    def __init__(self, parent=None):
        super(ZincWidgetState, self).__init__(parent)
        self._initialized_view = False
        self._active_handler = None
        self._handlers = {}

    def getActiveModeType(self):
        return self._active_handler.getModeType()

    def setActiveModeType(self, mode):
        if (self._active_handler is None or mode != self._active_handler.getModeType()) and mode in self._handlers:
            if not self._active_handler is None:
                self._active_handler.leave()
            self._active_handler = self._handlers[mode]
            self._active_handler.enter()

    def getMode(self, mode_type='ACTIVE'):
        """
        Returns the mode specified by mode_type.  If the
        specified mode is not in the _handlers dict then it
        returns the currently active mode.
        """
        if mode_type in self._handlers:
            return self._handlers[mode_type]

        return self._active_handler

    def addHandler(self, handler):
        handler.setZincView(self)
        self._handlers[handler.getModeType()] = handler

    def viewAll(self):
        self._active_handler.viewAll()

    def mousePressEvent(self, event):
        self._active_handler.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self._active_handler.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._active_handler.mouseReleaseEvent(event)

    def setPlane(self, plane):
        self._plane = plane
        self._plane.notifyChange.addObserver(self.setViewToPlane)

    def setViewToPlane(self):
        if self._sceneviewer is not None:
            normal = self._plane.getNormal()
            centre = self._plane.getRotationPoint()
            eye, lookat, up, angle = self.getViewParameters()
            scale = magnitude(sub(eye, lookat))
            self._sceneviewer.beginChange()
            self.setViewParameters(add(mult(normal, scale), centre), centre, up, angle)
            if not self._initialized_view:
                self._sceneviewer.viewAll()
                self._initialized_view = True
            self._sceneviewer.endChange()
