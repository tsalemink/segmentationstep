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
from mapclientplugins.segmentationstep.widgets.segmentationtab import SegmentationTab
from mapclientplugins.segmentationstep.widgets.ui_segmentationtab2d import Ui_SegmentationTab2D
from mapclientplugins.segmentationstep.widgets.definitions import ViewMode

class SegmentationTab2D(SegmentationTab):
    '''
    classdocs
    '''


    def __init__(self, context, undo_redo_stack, shared_context):
        '''
        Constructor
        '''
        super(SegmentationTab2D, self).__init__(undo_redo_stack)
        self._ui = Ui_SegmentationTab2D()
        self._ui.setupUi(self, shared_context)
        self._plane = None
        self._ui._sceneviewer.setContext(context)
        self._ui._sceneviewer.setUndoRedoStack(undo_redo_stack)

        self._makeConnections()

    def _makeConnections(self):
        self._ui._sceneviewer.graphicsInitialized.connect(self._sceneviewerReady)

    def _sceneviewerReady(self):
        self._ui._sceneviewer.setActiveModeType(ViewMode.SEGMENT)
        tool = self._tools[ViewMode.SEGMENT]
        action = self._tool_map[tool]
        action.setChecked(True)
        self._active_tool = tool

    def setPlane(self, plane):
        self._ui._sceneviewer.setPlane(plane)

    def addTool(self, tool):
        super(SegmentationTab2D, self).addTool(tool)
        self._ui._sceneviewer.addMode(tool)

    def getZincWidget(self):
        return self._ui._sceneviewer


