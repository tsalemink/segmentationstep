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
from PySide2 import QtGui, QtWidgets, QtCore

class SegmentationTabBar(QtWidgets.QTabBar):

    tabReorderRequested = QtCore.Signal(int, int)
    tabMoveRequested = QtCore.Signal(int)
    tabDetachRequested = QtCore.Signal(int, QtCore.QPoint)

    def __init__(self, parent=None):
        super(SegmentationTabBar, self).__init__(parent)
        self._start_drag_pos = None
        self._stop_drag_pos = None
#         self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._start_drag_pos = event.pos()
        super(SegmentationTabBar, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # make sure left mouse button is still down
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return

        # check if distance of drag is too small
        if (event.pos() - self._start_drag_pos).manhattanLength() < QtWidgets.QApplication.startDragDistance():
            return

        drag = QtGui.QDrag(self)
        mime = QtCore.QMimeData()
        pix = QtGui.QPixmap.grabWindow(self.parentWidget().currentWidget().winId()).scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        target_pix = QtGui.QPixmap(pix.size())
        painter = QtGui.QPainter(target_pix)
        painter.setOpacity(0.5)
        painter.drawPixmap(0, 0, pix)
        painter.end()
        drag.setPixmap(target_pix)
        mime.setData('application/tab-moving', b'tab moving data')
        drag.setMimeData(mime)
        d = drag.exec_()
        super(SegmentationTabBar, self).mouseMoveEvent(event)
        if d == QtCore.Qt.IgnoreAction:
            fromIndex = self.tabAt(self._start_drag_pos)
            event.accept()
            self.tabDetachRequested.emit(fromIndex, self._stop_drag_pos)
        elif d == QtCore.Qt.MoveAction:
            fromIndex = self.tabAt(self._start_drag_pos)
            if drag.target() == self:
                toIndex = self.tabAt(self._stop_drag_pos)
                self.tabReorderRequested.emit(fromIndex, toIndex)
            else:
                self.tabMoveRequested.emit(fromIndex)
                drag.target().addTab(self.parentWidget().currentWidget(), self.parentWidget().tabText(fromIndex))
            event.accept()


