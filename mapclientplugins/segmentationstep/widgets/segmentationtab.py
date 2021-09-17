"""
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
"""
from PySide2 import QtWidgets

class SegmentationTab(QtWidgets.QWidget):

    def __init__(self, undo_redo_stack, parent=None):
        """
        Constructor
        """
        super(SegmentationTab, self).__init__(parent)
        self._undo_redo_stack = undo_redo_stack

        self._active_handler = None
        self._handlers = {}
        self._action_map = {}
        self._handler_map = {}

    def addHandler(self, name, icon, handler):
        action = self._ui._tabToolBar.addAction(icon, name)
        action.setCheckable(True)
        self._action_map[action] = handler
        self._handler_map[handler] = action
        self._handlers[handler.getModeType()] = handler

    def add_command(self, name, icon, function):
        action = self._ui._tabToolBar.addAction(icon, name)
        self._action_map[action] = function
