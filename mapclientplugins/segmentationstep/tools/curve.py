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
from PySide2 import QtGui

from mapclientplugins.segmentationstep.tools.segmentation import SegmentationTool
from mapclientplugins.segmentationstep.definitions import ViewType, \
    DEFAULT_PUSH_PULL_STEP_SIZE, CURVE_GRAPHIC_NAME, CURVE_ON_PLANE_GRAPHIC_NAME, \
    DEFAULT_INTERPOLATION_COUNT, INTERPOLATION_POINT_GRAPHIC_NAME, \
    INTERPOLATION_POINT_ON_PLANE_GRAPHIC_NAME
from mapclientplugins.segmentationstep.tools.handlers.curve2d import Curve2D
from mapclientplugins.segmentationstep.tools.handlers.curve3d import Curve3D
from mapclientplugins.segmentationstep.tools.widgets.curve import PropertiesWidget
from mapclientplugins.segmentationstep.zincutils import getGlyphSize, \
    setGlyphSize
from mapclientplugins.segmentationstep.undoredo import CommandSetGlyphSize, \
    CommandSetSingleParameterMethod, CommandPushPullCurve, CommandDeleteCurve

class CurveTool(SegmentationTool):

    def __init__(self, plane, undo_redo_stack):
        super(CurveTool, self).__init__('Curve', undo_redo_stack)
        self._icon = QtGui.QIcon(':/toolbar_icons/curve.png')
        self._plane = plane
        self._widget = PropertiesWidget(self)
        self._handlers[ViewType.VIEW_2D] = Curve2D(plane, undo_redo_stack)
        self._handlers[ViewType.VIEW_3D] = Curve3D(plane, undo_redo_stack)
        self._step_size = DEFAULT_PUSH_PULL_STEP_SIZE
        self._interpolation_count = DEFAULT_INTERPOLATION_COUNT

    def setGetDimensionsMethod(self, get_dimensions_method):
        self._handlers[ViewType.VIEW_2D].setGetDimensionsMethod(get_dimensions_method)

    def setModel(self, model):
        self._model = model
        self._handlers[ViewType.VIEW_2D].setModel(model)
        self._handlers[ViewType.VIEW_3D].setModel(model)

    def setScene(self, scene):
        self._scene = scene
        self._handlers[ViewType.VIEW_2D].setScene(scene)
        self._handlers[ViewType.VIEW_3D].setScene(scene)

    def pointSizeChanged(self, value):
        glyph = self._scene.getGraphic(CURVE_GRAPHIC_NAME)
        current = getGlyphSize(glyph)
        new = [value, value, value]

        if current != new:
            glyphs = [glyph, self._scene.getGraphic(CURVE_ON_PLANE_GRAPHIC_NAME),
                      self._scene.getGraphic(INTERPOLATION_POINT_GRAPHIC_NAME),
                      self._scene.getGraphic(INTERPOLATION_POINT_ON_PLANE_GRAPHIC_NAME)]
            c = CommandSetGlyphSize(current, new, glyphs)
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

    def interpolationCountChanged(self, value):
        if value != self._interpolation_count:
            c = CommandSetSingleParameterMethod(self._interpolation_count, value)
            c.setSingleParameterMethod(self._setInterpolationCount)
            self._interpolation_count = value

            self._undo_redo_stack.push(c)

    def _setInterpolationCount(self, value):
        self._widget._ui._spinBoxInterpolationCount.blockSignals(True)
        self._widget._ui._spinBoxInterpolationCount.setValue(value)
        self._widget._ui._spinBoxInterpolationCount.blockSignals(False)
        self._handlers[ViewType.VIEW_2D].setInterpolationCount(value)
        self._handlers[ViewType.VIEW_3D].setInterpolationCount(value)

    def _filterNodes(self, node_ids):
        curve_nodes = []
        group = self._model.getCurveGroup()
        for node_id in node_ids:
            node = self._model.getNodeByIdentifier(node_id)
            if group.containsNode(node):
                curve_nodes.append(node_id)

        return curve_nodes

    def deleteClicked(self):
        selection_curve = self._filterNodes(self._model.getCurrentSelection())

        if selection_curve:
            c = CommandDeleteCurve(self._model, selection_curve)
            c.setScene(self._scene)
            self._undo_redo_stack.push(c)

    def pushDownClicked(self):
        self._pushPullNodes(-1.0)

    def pullUpClicked(self):
        self._pushPullNodes(1.0)

    def _pushPullNodes(self, direction):
        current_selection = self._filterNodes(self._model.getCurrentSelection())
        if current_selection:
            value = self._widget._ui._doubleSpinBoxStepSize.value()
            scale = value * direction
            c = CommandPushPullCurve(self._model, current_selection, scale)
            c.setSetRotationPointMethod(self._plane.setRotationPoint)
            c.setSetNormalMethod(self._plane.setNormal)
            c.setScene(self._scene)
            self._undo_redo_stack.push(c)


