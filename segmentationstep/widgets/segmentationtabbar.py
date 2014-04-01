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
from PySide import QtGui, QtCore

class SegmentationTabBar(QtGui.QTabBar):

    def __init__(self, parent=None):
        super(SegmentationTabBar, self).__init__(parent)
        self._start_drag_pos = None
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        super(SegmentationTabBar, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.LeftButton:
            self._start_drag_pos = event.pos()

    def mouseMoveEvent(self, event):
        # make sure left mouse button is still down
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return

        # check if distance of drag is too small
        if (event.pos() - self._start_drag_pos).manhattanLength() < QtGui.QApplication.startDragDistance():
            return

        print('good to go.')
