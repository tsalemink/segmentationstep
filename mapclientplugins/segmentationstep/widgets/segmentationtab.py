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

class SegmentationTab(QtGui.QWidget):

    def __init__(self, undo_redo_stack, parent=None):
        '''
        Constructor
        '''
        super(SegmentationTab, self).__init__(parent)
        self._undo_redo_stack = undo_redo_stack

        self._active_tool = None
        self._tools = {}
        self._action_map = {}
        self._tool_map = {}

    def addTool(self, tool):
        action = self._ui._tabToolBar.addAction(tool.getIcon(), tool.getName())
        action.setCheckable(True)
        self._action_map[action] = tool
        self._tool_map[tool] = action
        self._tools[tool.getModeType()] = tool

    def changeTool(self, tool):
        if tool != self._active_tool:
            old_action = self._tool_map[self._active_tool]
            old_action.setChecked(False)
            current_action = self._tool_map[tool]
            current_action.setChecked(True)
            self._active_tool = tool

    def _toolbarAction(self):
        print(self.sender())


