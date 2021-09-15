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
from mapclientplugins.segmentationstep.widgets.segmentationtab import SegmentationTab
from mapclientplugins.segmentationstep.widgets.ui_sceneviewertab import Ui_SceneviewerTab
from mapclientplugins.segmentationstep.definitions import ViewMode
from mapclientplugins.segmentationstep.undoredo import CommandChangeViewHandler

class SceneviewerTab(SegmentationTab):
    """
    classdocs
    """

    def __init__(self, context, undo_redo_stack, shared_context=None):
        """
        Constructor
        """
        super(SceneviewerTab, self).__init__(undo_redo_stack)
        self._ui = Ui_SceneviewerTab()
        self._ui.setupUi(self)
        self._plane = None
        self._ui._zincwidget.setContext(context)
        self._ui._zincwidget.setUndoRedoStack(undo_redo_stack)

        self._makeConnections()

    def _makeConnections(self):
        self._ui._zincwidget.graphicsInitialized.connect(self._sceneviewerReady)
        self._ui._tabToolBar.actionTriggered.connect(self._toolbarAction)

    def _toolbarAction(self, action):
        if action.isCheckable():
            new_handler = self._action_map[action]
            if new_handler == self._active_handler:
                action.blockSignals(True)
                action.setChecked(True)
                action.blockSignals(False)
            else:
                current_action = self._handler_map[self._active_handler]
                current_handler = self._active_handler
                c = CommandChangeViewHandler(current_handler, current_action, new_handler, action)
                c.setSetChangeHandlerMethod(self._changeHandler)

                self._undo_redo_stack.push(c)

        else:
            function = self._action_map[action]
            function()

    def _changeHandler(self, handler):
        self._active_handler = handler
        self._ui._zincwidget.setActiveModeType(handler.getModeType())

    def setActiveHandler(self, handler_type):
        if handler_type in self._handlers:
            handler = self._handlers[handler_type]
            if self._active_handler is not None and handler != self._active_handler:
                action = self._handler_map[handler]
                current_action = self._handler_map[self._active_handler]
                current_handler = self._active_handler
                c = CommandChangeViewHandler(current_handler, current_action, handler, action)
                c.setSetChangeHandlerMethod(self._changeHandler)

                self._undo_redo_stack.push(c)


    def _sceneviewerReady(self):
        self._ui._zincwidget.setActiveModeType(ViewMode.SEGMENT_POINT)
        tool = self._handlers[ViewMode.SEGMENT_POINT]
        action = self._handler_map[tool]
        action.setChecked(True)
        self._active_handler = tool

        # Trying to find a way to have everything in the one place
        # including the sceneviewers added using designer.
        if hasattr(self._ui._zincwidget, '_plane'):
            self._ui._zincwidget.setTumbleRate(0.0)
            self._ui._zincwidget.setViewToPlane()

    def setPlane(self, plane):
        self._ui._zincwidget.setPlane(plane)

    def addHandler(self, name, icon, handler):
        super(SceneviewerTab, self).addHandler(name, icon, handler)
        self._ui._zincwidget.addHandler(handler)

    def getZincWidget(self):
        return self._ui._zincwidget


