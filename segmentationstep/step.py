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
import os

from PySide import QtGui, QtCore

from mapclient.mountpoints.workflowstep import WorkflowStepMountPoint

from segmentationstep.widgets.segmentationwidget import SegmentationWidget
from segmentationstep.widgets.configuredialog import ConfigureDialog, ConfigureDialogState

STEP_SERIALISATION_FILENAME = 'step.conf'

class SegmentationStep(WorkflowStepMountPoint):
    '''
    A step that acts like the step plugin duck
    '''

    def __init__(self, location):
        '''
        Constructor
        '''
        super(SegmentationStep, self).__init__('Segmentation', location)
        self._identifier = ''
        self._icon = QtGui.QImage(':/segmentation/icons/seg.gif')
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port', 'http://physiomeproject.org/workflow/1.0/rdf-schema#uses', 'http://physiomeproject.org/workflow/1.0/rdf-schema#images'))
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port', 'http://physiomeproject.org/workflow/1.0/rdf-schema#provides', 'http://physiomeproject.org/workflow/1.0/rdf-schema#pointcloud'))
        self._widget = None
        self._dataIn = None
#        self._configured = True
        self._state = ConfigureDialogState()

    def configure(self):
        d = ConfigureDialog(self._state)
        d.setModal(True)
        if d.exec_():
            self._state = d.getState()

        self._configured = d.validate()
        if self._configured and self._configuredObserver != None:
            self._configuredObserver()

    def getIdentifier(self):
        return self._state.identifier()

    def setIdentifier(self, identifier):
        self._state.setIdentifier(identifier)

    def serialize(self, location):
        self._step_location = os.path.join(location, self._state.identifier())
        if not os.path.exists(self._step_location):
            os.mkdir(self._step_location)

        s = QtCore.QSettings(os.path.join(self._step_location, STEP_SERIALISATION_FILENAME), QtCore.QSettings.IniFormat)
        self._state.save(s)

    def deserialize(self, location):
        self._step_location = os.path.join(location, self._state.identifier())
        s = QtCore.QSettings(os.path.join(self._step_location, STEP_SERIALISATION_FILENAME), QtCore.QSettings.IniFormat)
        self._state.load(s)
        d = ConfigureDialog(self._state)
        self._configured = d.validate()

    def setPortOutput(self, portId, dataIn):
        self._dataIn = dataIn

    def getPortOutput(self, portId):
        return self._widget.getPointCloud()

    def execute(self):
        if not self._widget:
            self._widget = SegmentationWidget(self._dataIn)
            self._widget._ui.doneButton.clicked.connect(self._doneExecution)

        self._setCurrentUndoRedoStack(self._widget.undoRedoStack())
        self._setCurrentWidget(self._widget)
