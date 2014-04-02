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

from segmentationstep.widgets.segmentationtabwidget import SegmentationTabWidget

class SegmentationTabDropWidget(QtGui.QWidget):

    def __init__(self, parent):
        super(SegmentationTabDropWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self._animation_increase = QtCore.QPropertyAnimation(self, 'maximumWidth')
        self._animation_increase.setStartValue(1)
        self._animation_increase.setEndValue(100)
        self._animation_decrease = QtCore.QPropertyAnimation(self, 'maximumWidth')
        self._animation_decrease.setStartValue(100)
        self._animation_decrease.setEndValue(1)
        self._animation_decrease.finished.connect(self._animationFinished)
        self._tabWidget = None

    def _animationFinished(self):
        self.setStyleSheet("")

    def dragEnterEvent(self, event):
        super(SegmentationTabDropWidget, self).dragEnterEvent(event)
        m = event.mimeData()
        if m.hasFormat('application/tab-moving'):
            event.acceptProposedAction()
            if self.width() < 100:
                self._animation_increase.setStartValue(self.width())
                self.setStyleSheet("background-color: rgb(107, 186, 255);")
                self._animation_increase.start()

    def dragLeaveEvent(self, event):
        super(SegmentationTabDropWidget, self).dragLeaveEvent(event)
        if self.width() > 1:
            self._animation_decrease.setStartValue(self.width())
            self._animation_decrease.start()

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)

    def dropEvent(self, event):
        m = event.mimeData()
        if m.hasFormat('application/tab-moving'):
            event.acceptProposedAction()

        super(SegmentationTabDropWidget, self).dropEvent(event)

    def addTab(self, widget, text):
        if self._tabWidget is None:
            v_layout = QtGui.QVBoxLayout()
            v_layout.setContentsMargins(0, 0, 0, 0)
            self._tabWidget = SegmentationTabWidget(self)
#             moveWidget = widget.widget(index)
            self._tabWidget.addTab(widget, text)
#             moveWidget.setParent(self._tabWidget)
#             self._tabWidget.resize(300, 200)
            v_layout.addWidget(self._tabWidget)
            self.setLayout(v_layout)
            self.setMaximumWidth(16777215)
#             moveWidget.show()
            self._tabWidget.show()


