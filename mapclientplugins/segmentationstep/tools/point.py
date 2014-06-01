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

from mapclientplugins.segmentationstep.definitions import ViewType
from mapclientplugins.segmentationstep.tools.segmentation import SegmentationTool
from mapclientplugins.segmentationstep.tools.handlers.point2d import Point2D
from mapclientplugins.segmentationstep.tools.handlers.point3d import Point3D
from mapclientplugins.segmentationstep.tools.widgets.point import PropertiesWidget, DEFAULT_STEP_SIZE
from mapclientplugins.segmentationstep.zincutils import getGlyphSize, setGlyphSize
from mapclientplugins.segmentationstep.undoredo import CommandSetGlyphSize, CommandSetSingleParameterMethod, CommandDelete, CommandPushPull
from mapclientplugins.segmentationstep.definitions import POINT_CLOUD_GRAPHIC_NAME

class PointTool(SegmentationTool):

    def __init__(self, plane, undo_redo_stack):
        super(PointTool, self).__init__('Point', undo_redo_stack)
        self._icon = QtGui.QIcon(':/toolbar_icons/point.png')
        self._handlers[ViewType.VIEW_2D] = Point2D(plane, undo_redo_stack)
        self._handlers[ViewType.VIEW_3D] = Point3D(plane, undo_redo_stack)
        self._widget = PropertiesWidget(self)
        self._model = None
        self._plane = plane
        self._step_size = DEFAULT_STEP_SIZE

    def setGetDimensionsMethod(self, get_dimensions_method):
        self._handlers[ViewType.VIEW_2D].setGetDimensionsMethod(get_dimensions_method)

    def setModel(self, model):
        self._model = model
        self._handlers[ViewType.VIEW_2D].setModel(model)
        self._handlers[ViewType.VIEW_3D].setModel(model)

    def setScene(self, scene):
        self._scene = scene

    def pointSizeChanged(self, value):
        glyph = self._scene.getGraphic(POINT_CLOUD_GRAPHIC_NAME)
        current = getGlyphSize(glyph)
        new = [value, value, value]

        if current != new:
            c = CommandSetGlyphSize(current, new, glyph)
            c.setSetGlyphSizeMethod(setGlyphSize)
            c.setSpinBox(self._widget._ui._doubleSpinBoxPointSize)

            self._undo_redo_stack.push(c)

    def stepSizeChanged(self, value):
        if value != self._step_size:
            c = CommandSetSingleParameterMethod(self._step_size, value)
            c.setSingleParameterMethod(self._setStepSize)
            self._step_size = value

            self._undo_redo_stack.push(c)

    def _setStepSize(self, value):
        self._widget._ui._doubleSpinBoxStepSize.blockSignals(True)
        self._widget._ui._doubleSpinBoxStepSize.setValue(value)
        self._widget._ui._doubleSpinBoxStepSize.blockSignals(False)

    def streamingCreateChanged(self, state):
        new = True if state == 2 else False
        current = not new
        c = CommandSetSingleParameterMethod(current, new)
        c.setSingleParameterMethod(self._setStreamingCreate)

        self._undo_redo_stack.push(c)

    def _setStreamingCreate(self, state):
        self._handlers[ViewType.VIEW_2D].setStreamingCreate(state)
        self._handlers[ViewType.VIEW_3D].setStreamingCreate(state)
        self._widget._ui._checkBoxStreamingCreate.blockSignals(True)
        self._widget._ui._checkBoxStreamingCreate.setChecked(state)
        self._widget._ui._checkBoxStreamingCreate.blockSignals(False)

    def deleteClicked(self):
        c = CommandDelete(self._model, self._model.getCurrentSelection())
        self._undo_redo_stack.push(c)

    def pushDownClicked(self):
        self._pushPullNodes(-1.0)

    def pullUpClicked(self):
        self._pushPullNodes(1.0)

    def _pushPullNodes(self, direction):
        value = self._widget._ui._doubleSpinBoxStepSize.value()
        scale = value * direction
        c = CommandPushPull(self._model, self._model.getCurrentSelection(), scale)
        c.setSetRotationPointMethod(self._plane.setRotationPoint)
        self._undo_redo_stack.push(c)


