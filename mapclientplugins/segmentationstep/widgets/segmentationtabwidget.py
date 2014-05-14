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

from PySide import QtCore, QtGui
from mapclientplugins.segmentationstep.widgets.segmentationtabbar import SegmentationTabBar

TABWIDGET_TARGET_SIZE = 100

class SegmentationTabWidget(QtGui.QTabWidget):

    def __init__(self, parent=None):
        super(SegmentationTabWidget, self).__init__(parent)
        tb = SegmentationTabBar()
        tb.tabReorderRequested.connect(self.repositionTab)
        self.setTabBar(tb)

        self.setAcceptDrops(True)

        self._animation_increase = QtCore.QPropertyAnimation(self, 'maximumWidth')
        self._animation_increase.setStartValue(1)
        self._animation_increase.setEndValue(TABWIDGET_TARGET_SIZE)
        self._animation_decrease = QtCore.QPropertyAnimation(self, 'maximumWidth')
        self._animation_decrease.setStartValue(TABWIDGET_TARGET_SIZE)
        self._animation_decrease.setEndValue(1)
        self._animation_decrease.finished.connect(self._animationFinished)

    def _animationFinished(self):
        self.setStyleSheet("")

    def repositionTab(self, fromIndex, toIndex):
        w = self.widget(fromIndex);
        icon = self.tabIcon(fromIndex);
        text = self.tabText(fromIndex);

        self.removeTab(fromIndex);
        self.insertTab(toIndex, w, icon, text);
        self.setCurrentIndex(toIndex);

    def dragEnterEvent(self, event):
        m = event.mimeData()
        if m.hasFormat('application/tab-moving'):
            event.acceptProposedAction()
            if self.width() < TABWIDGET_TARGET_SIZE:
                self._animation_increase.setStartValue(self.width())
                self.setStyleSheet("background-color: rgb(107, 186, 255);")
                self._animation_increase.start()

    def dragLeaveEvent(self, event):
#         super(SegmentationTabDropWidget, self).dragLeaveEvent(event)
        if self.width() > 1 and self.count() == 0:
            self._animation_decrease.setStartValue(self.width())
            self._animation_decrease.start()

    def dragMoveEvent(self, event):
        m = event.mimeData()
        if m.hasFormat('application/tab-moving'):
            self._stop_drag_pos = event.pos()
            event.acceptProposedAction()

#         super(SegmentationTabWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        m = event.mimeData()
        if m.hasFormat('application/tab-moving'):
            event.acceptProposedAction()

    def tabInserted(self, index):
        if self.count() == 1:
            self.setStyleSheet("")
            self._animation_increase.setEndValue(16777215)
            self._animation_increase.start()

    def tabRemoved(self, index):
        if self.count() == 0:
            self._animation_increase.setEndValue(TABWIDGET_TARGET_SIZE)
            self._animation_decrease.start()


