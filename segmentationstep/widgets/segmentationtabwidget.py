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
from segmentationstep.widgets.segmentationtabbar import SegmentationTabBar

class SegmentationTabWidget(QtGui.QTabWidget):

    def __init__(self, parent=None):
        super(SegmentationTabWidget, self).__init__(parent)
        tb = SegmentationTabBar()
        tb.tabReorderRequested.connect(self.repositionTab)
        self.setTabBar(tb)

        self.setAcceptDrops(True)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
#         sizePolicy.setVerticalStretch(1)
#         sizePolicy.setHeightForWidth(self._tabWidget1.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

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

#         super(SegmentationTabWidget, self).dragEnterEvent(event)

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

#         super(SegmentationTabWidget, self).dropEvent(event)
#     def dragEnterEvent(self, event):
#         print('yooyoyoyoyoyo')
#         m = event.mimeData()
#         f = m.formats()
#         if 'action' in f and m.data('action') == 'application/tab-moving':
#             print 'tab widget accept p action'
#             event.acceptProposedAction()
#
#     def dropEvent(self, event):
#         print('kdkdkddkdk')
#         fromIndex = self.tabAt(self._start_drag_pos)
#         toIndex = self.tabAt(event.pos())
#         print fromIndex, toIndex

