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
from PySide import QtCore

from mapclientplugins.segmentationstep.zincutils import button_map, modifier_map, Sceneviewerinput
from mapclientplugins.segmentationstep.undoredo import CommandChangeView

class AbstractTool(object):


    def __init__(self, view, plane, undo_redo_stack):
        self._mode_type = None
        self._view = view
        self._plane = plane
        self._undo_redo_stack = undo_redo_stack
        self._get_dimension_method = None

    def setGetDimensionsMethod(self, get_dimensions_method):
        self._get_dimension_method = get_dimensions_method

    def leave(self):
        pass

    def enter(self):
        pass

    def getModeType(self):
        return self._mode_type

    def getIcon(self):
        raise NotImplementedError()

    def getName(self):
        return 'Tool'

    def viewAll(self):
        p1 = self._view.getViewParameters()
        self._view.getSceneviewer().viewAll()
        p2 = self._view.getViewParameters()
        c = CommandChangeView(p1, p2)
        c.setCallbackMethod(self._view.setViewParameters)
        self._undo_redo_stack.push(c)

    def mousePressEvent(self, event):
        sceneviewer = self._view.getSceneviewer()
        scene_input = sceneviewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_PRESS)
        scene_input.setButtonType(button_map[event.button()])
        scene_input.setModifierFlags(modifier_map(event.modifiers()))

        sceneviewer.processSceneviewerinput(scene_input)
        self._start_view_parameters = self._view.getViewParameters()

    def mouseMoveEvent(self, event):
        sceneviewer = self._view.getSceneviewer()
        scene_input = sceneviewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_MOTION_NOTIFY)
        if event.type() == QtCore.QEvent.Leave:
            scene_input.setPosition(-1, -1)

        sceneviewer.processSceneviewerinput(scene_input)

    def mouseReleaseEvent(self, event):
        sceneviewer = self._view.getSceneviewer()
        scene_input = sceneviewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
        scene_input.setButtonType(button_map[event.button()])

        sceneviewer.processSceneviewerinput(scene_input)
        end_view_parameters = self._view.getViewParameters()
        c = CommandChangeView(self._start_view_parameters, end_view_parameters)
        c.setCallbackMethod(self._view.setViewParameters)
        self._undo_redo_stack.push(c)

