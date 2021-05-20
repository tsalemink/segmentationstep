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
from PySide2 import QtWidgets

from mapclientplugins.segmentationstep.tools.resources.ui_point import Ui_PropertiesWidget
from mapclientplugins.segmentationstep.definitions import DEFAULT_SEGMENTATION_POINT_SIZE, \
    DEFAULT_PUSH_PULL_STEP_SIZE

class PropertiesWidget(QtWidgets.QWidget):

    def __init__(self, tool):
        super(PropertiesWidget, self).__init__()
        self._ui = Ui_PropertiesWidget()
        self._ui.setupUi(self)

        self._ui._doubleSpinBoxPointSize.setValue(DEFAULT_SEGMENTATION_POINT_SIZE)
        self._ui._doubleSpinBoxStepSize.setValue(DEFAULT_PUSH_PULL_STEP_SIZE)

        self._tool = tool

        self._makeConnections()

    def _makeConnections(self):
        self._ui._doubleSpinBoxPointSize.valueChanged.connect(self._tool.pointSizeChanged)
        self._ui._doubleSpinBoxStepSize.valueChanged.connect(self._tool.stepSizeChanged)
        self._ui._checkBoxStreamingCreate.stateChanged.connect(self._tool.streamingCreateChanged)
        self._ui._pushButtonDelete.clicked.connect(self._tool.deleteClicked)
        self._ui._pushButtonPullUp.clicked.connect(self._tool.pullUpClicked)
        self._ui._pushButtonPushDown.clicked.connect(self._tool.pushDownClicked)


