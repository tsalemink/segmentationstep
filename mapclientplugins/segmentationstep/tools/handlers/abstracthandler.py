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
from mapclientplugins.segmentationstep.definitions import \
    IMAGE_PLANE_GRAPHIC_NAME, POINT_CLOUD_GRAPHIC_NAME, \
    ELEMENT_OUTLINE_GRAPHIC_NAME, SELECTION_BOX_3D_GRAPHIC_NAME, \
    ELEMENT_NODE_LABEL_GRAPHIC_NAME, CURVE_GRAPHIC_NAME, \
    PLANE_MANIPULATION_SPHERE_GRAPHIC_NAME, \
    PLANE_MANIPULATION_NORMAL_GRAPHIC_NAME

class AbstractHandler(object):

    def __init__(self, plane, undo_redo_stack):
        self._mode_type = None
        self._zinc_view = None
        self._plane = plane
        self._undo_redo_stack = undo_redo_stack
        self._get_dimension_method = None
        self._sceneviewer_filter = None
        self._scenepicker_filter = None
        self._active_button = QtCore.Qt.NoButton

    def setGetDimensionsMethod(self, get_dimensions_method):
        self._get_dimension_method = get_dimensions_method

    def setZincView(self, zinc_view):
        self._zinc_view = zinc_view

    def enter(self):
        sceneviewer = self._zinc_view.getSceneviewer()
        self._sceneviewer_filter_orignal = sceneviewer.getScenefilter()
        if self._sceneviewer_filter is None:
            self._sceneviewer_filter = self._createSceneviewerFilter()

        sceneviewer.setScenefilter(self._sceneviewer_filter)

        scenepicker = self._zinc_view.getScenepicker()
        self._scenepicker_filter_original = scenepicker.getScenefilter()
        if self._scenepicker_filter is None:
            self._scenepicker_filter = self._createScenepickerFilter()

        scenepicker.setScenefilter(self._scenepicker_filter)

    def leave(self):
        sceneviewer = self._zinc_view.getSceneviewer()
        sceneviewer.setScenefilter(self._sceneviewer_filter_orignal)
        scenepicker = self._zinc_view.getScenepicker()
        scenepicker.setScenefilter(self._scenepicker_filter_original)

    def getModeType(self):
        return self._mode_type

    def getIcon(self):
        raise NotImplementedError()

    def getName(self):
        return 'Tool'

    def viewAll(self):
        p1 = self._zinc_view.getViewParameters()
        self._zinc_view.getSceneviewer().viewAll()
        p2 = self._zinc_view.getViewParameters()
        c = CommandChangeView(p1, p2)
        c.setCallbackMethod(self._zinc_view.setViewParameters)
        self._undo_redo_stack.push(c)

    def mousePressEvent(self, event):
        sceneviewer = self._zinc_view.getSceneviewer()
        scene_input = sceneviewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_PRESS)
        scene_input.setButtonType(button_map[event.button()])
        scene_input.setModifierFlags(modifier_map(event.modifiers()))

        sceneviewer.processSceneviewerinput(scene_input)
        self._start_view_parameters = self._zinc_view.getViewParameters()

    def mouseMoveEvent(self, event):
        sceneviewer = self._zinc_view.getSceneviewer()
        scene_input = sceneviewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_MOTION_NOTIFY)
        if event.type() == QtCore.QEvent.Leave:
            scene_input.setPosition(-1, -1)

        sceneviewer.processSceneviewerinput(scene_input)

    def mouseReleaseEvent(self, event):
        sceneviewer = self._zinc_view.getSceneviewer()
        scene_input = sceneviewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
        scene_input.setButtonType(button_map[event.button()])

        sceneviewer.processSceneviewerinput(scene_input)
        end_view_parameters = self._zinc_view.getViewParameters()
        c = CommandChangeView(self._start_view_parameters, end_view_parameters)
        c.setCallbackMethod(self._zinc_view.setViewParameters)
        self._undo_redo_stack.push(c)

    def _createSceneviewerFilter(self):
        sceneviewer = self._zinc_view.getSceneviewer()
        scene = sceneviewer.getScene()
        filtermodule = scene.getScenefiltermodule()

        visibility_filter = filtermodule.createScenefilterVisibilityFlags()
        name_filter1 = filtermodule.createScenefilterGraphicsName(IMAGE_PLANE_GRAPHIC_NAME)
        name_filter2 = filtermodule.createScenefilterGraphicsName(POINT_CLOUD_GRAPHIC_NAME)
        name_filter3 = filtermodule.createScenefilterGraphicsName(CURVE_GRAPHIC_NAME)
        name_filter4 = filtermodule.createScenefilterGraphicsName(ELEMENT_OUTLINE_GRAPHIC_NAME)
        name_filter5 = filtermodule.createScenefilterGraphicsName(ELEMENT_NODE_LABEL_GRAPHIC_NAME)
        name_filter6 = filtermodule.createScenefilterGraphicsName(SELECTION_BOX_3D_GRAPHIC_NAME)
        name_filter7 = filtermodule.createScenefilterGraphicsName(PLANE_MANIPULATION_NORMAL_GRAPHIC_NAME)
        name_filter8 = filtermodule.createScenefilterGraphicsName(PLANE_MANIPULATION_SPHERE_GRAPHIC_NAME)

        name_filter = filtermodule.createScenefilterOperatorOr()
        name_filter.appendOperand(name_filter1)
        name_filter.appendOperand(name_filter2)
        name_filter.appendOperand(name_filter3)
        name_filter.appendOperand(name_filter4)
        name_filter.appendOperand(name_filter5)
        name_filter.appendOperand(name_filter6)
        name_filter.appendOperand(name_filter7)
        name_filter.appendOperand(name_filter8)

        master_filter = filtermodule.createScenefilterOperatorAnd()
        master_filter.appendOperand(visibility_filter)
        master_filter.appendOperand(name_filter)

        return master_filter

    def _createScenepickerFilter(self):
        sceneviewer = self._zinc_view.getSceneviewer()
        scene = sceneviewer.getScene()
        filtermodule = scene.getScenefiltermodule()
        visibility_filter = filtermodule.createScenefilterVisibilityFlags()

        return visibility_filter


