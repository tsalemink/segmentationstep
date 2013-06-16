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

from segmentationstep.widgets.ui_segmentationwidget import Ui_SegmentationWidget

class SegmentationWidget(QtGui.QWidget):
    '''
    About dialog to display program about information.
    '''


    def __init__(self, imageDataLocation, parent=None):
        '''
        Constructor
        '''
        QtGui.QWidget.__init__(self, parent)
        self._ui = Ui_SegmentationWidget()
        self._ui.setupUi(self)
        self._ui.actionButton.setText('Add Point(s)')
        self._ui.context.setImageDataLocation(imageDataLocation)

        self._makeConnections()

    def _makeConnections(self):
        self._ui.isoValueSlider.valueChanged.connect(self._ui.context.setSliderValue)
        self._ui.compComboBox.currentIndexChanged.connect(self._ui.context.setFieldComponent)
        self._ui.actionButton.clicked.connect(self._actionButtonClicked)

    def _actionButtonClicked(self):
        if self._ui.actionButton.text().startswith('Add'):
            self._ui.actionButton.setText('Adjust View')
        else:
            self._ui.actionButton.setText('Add Point(s)')

        self._ui.context.actionButtonClicked()

    def undoRedoStack(self):
        return self._ui.context._undoRedoStack

    def getPointCloud(self):
        return self._ui.context.getPointCloud()
