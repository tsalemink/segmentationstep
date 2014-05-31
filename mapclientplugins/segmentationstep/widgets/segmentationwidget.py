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
from PySide import QtGui, QtCore

from mapclientplugins.segmentationstep.tools import normal, orientation, point
from mapclientplugins.segmentationstep.widgets.ui_segmentationwidget import Ui_SegmentationWidget
from mapclientplugins.segmentationstep.undoredo import CommandChangeViewMode, CommandSetScale, CommandSetSingleParameterMethod, CommandSetGraphicVisibility, CommandSetGlyphSize
from mapclientplugins.segmentationstep.widgets.zincwidget import ProjectionMode
from mapclientplugins.segmentationstep.definitions import ViewMode, ELEMENT_OUTLINE_GRAPHIC_NAME, IMAGE_PLANE_GRAPHIC_NAME, ELEMENT_NODE_LABEL_GRAPHIC_NAME
from mapclientplugins.segmentationstep.widgets.segmentationstate import SegmentationState
from mapclientplugins.segmentationstep.zincutils import getGlyphSize, setGlyphSize
from mapclientplugins.segmentationstep.widgets.sceneviewertab import SceneviewerTab
from mapclientplugins.segmentationstep.scene.master import MasterScene

class FakeMouseEvent(object):

    def __init__(self, x, y):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y

class SegmentationWidget(QtGui.QWidget):
    '''
    About dialog to display program about information.
    '''


    def __init__(self, model, parent=None):
        '''
        Constructor
        '''
        QtGui.QWidget.__init__(self, parent)
        self._ui = Ui_SegmentationWidget()
        self._ui.setupUi(self)

        self._ui.splitterToolBox.setStretchFactor(0, 0)
        self._ui.splitterToolBox.setStretchFactor(1, 1)

        self._model = model
        self._scene = MasterScene(self._model)

        self._setupTabs()
        self._setupTools()

        self._debug_print = False

        self._timer = QtCore.QTimer()
#         self._timer.timeout.connect(self.falsifyMouseEvents)
#         self._timer.start(1000)
        self._counter = 0

        self._viewstate = None

        self._setupUi()

        self._makeConnections()

    def _makeConnections(self):
        self._ui._lineEditWidthScale.editingFinished.connect(self._scaleChanged)
        self._ui._lineEditHeightScale.editingFinished.connect(self._scaleChanged)
        self._ui._lineEditDepthScale.editingFinished.connect(self._scaleChanged)

        self._ui._checkBoxCoordinateLabels.clicked.connect(self._graphicVisibilityChanged)
        self._ui._checkBoxImageOutline.clicked.connect(self._graphicVisibilityChanged)
        self._ui._checkBoxImagePlane.clicked.connect(self._graphicVisibilityChanged)

    def _setupUi(self):
        dbl_validator = QtGui.QDoubleValidator()
        dbl_validator.setBottom(0.0)
        self._ui._lineEditWidthScale.setValidator(dbl_validator)
        self._ui._lineEditHeightScale.setValidator(dbl_validator)
        self._ui._lineEditDepthScale.setValidator(dbl_validator)

        dimensions = self._model.getImageModel().getDimensionsInPixels()
        self._ui._labelmageWidth.setText(str(dimensions[0]) + ' px')
        self._ui._labelmageHeight.setText(str(dimensions[1]) + ' px')
        self._ui._labelmageDepth.setText(str(dimensions[2]) + ' px')

    def _resetViewClicked(self):
        self._loadViewState()
        self._undoRedoStack.clear()

    def _saveViewState(self):
        eye, lookat, up, angle = self._ui._sceneviewer3d.getViewParameters()

        self._viewstate = SegmentationState()
        self._viewstate.setViewParameters(eye, lookat, up, angle)
#         self._viewstate.setPointOnPlane(self._getPointOnPlane())
#         self._viewstate.setPlaneNormal(self._getPlaneNormal())
        self._viewstate.setPlaneRotationMode(self._ui._sceneviewer3d.getActiveModeType())
        self._viewstate.setProjectionMode(self._ui._sceneviewer3d.getProjectionMode())
        self._viewstate.setPlaneNormalGlyphBaseSize(self._ui._doubleSpinBoxNormalArrow.value())
        self._viewstate.setPlaneRotationCentreGlyphBaseSize(self._ui._doubleSpinBoxRotationCentre.value())

    def _loadViewState(self):
        eye, lookat, up, angle = self._viewstate.getViewParameters()
        self._ui._sceneviewer3d.setViewParameters(eye, lookat, up, angle)
#         self._setPlaneEquation(self._viewstate.getPlaneNormal(), self._viewstate.getPointOnPlane())
        self._ui._sceneviewer3d.setActiveModeType(self._viewstate.getPlaneRotationMode())
        self._setProjectionMode(self._viewstate.getProjectionMode())
        base_size = self._viewstate.getPlaneNormalGlyphBaseSize()
        self._ui._doubleSpinBoxNormalArrow.setValue(base_size)
        self._setPlaneNormalGlyphBaseSize(base_size)
        base_size = self._viewstate.getPlaneRotationCentreGlyphBaseSize()
        self._ui._doubleSpinBoxRotationCentre.setValue(base_size)
        self._setPlaneRotationCentreGlyphBaseSize(base_size)

    def _projectionModeChanged(self):
        current_mode = ProjectionMode.PERSPECTIVE if self._ui._radioButtonParallel.isChecked() else ProjectionMode.PARALLEL
        new_mode = ProjectionMode.PARALLEL if self._ui._radioButtonParallel.isChecked() else ProjectionMode.PERSPECTIVE
        c = CommandSetSingleParameterMethod(current_mode, new_mode)
        c.setSingleParameterMethod(self._setProjectionMode)

        self._model.getUndoRedoStack().push(c)

    def _setProjectionMode(self, mode):
        self._ui._radioButtonParallel.setChecked(mode == ProjectionMode.PARALLEL)
        self._ui._radioButtonPerspective.setChecked(mode == ProjectionMode.PERSPECTIVE)
        self._ui._sceneviewer3d.setProjectionMode(mode)

    def _iconSizeChanged(self):
        current = 0.0
        spin_box = self.sender()
        if spin_box == self._ui._doubleSpinBoxNormalArrow:
            mode = self._ui._sceneviewer3d.getMode(ViewMode.PLANE_NORMAL)
            glyph = mode.getGlyph()
            current = getGlyphSize(glyph)
            base_size = self._ui._doubleSpinBoxNormalArrow.value()
            new = [base_size, base_size / 4, base_size / 4]
        elif spin_box == self._ui._doubleSpinBoxRotationCentre:
            mode = self._ui._sceneviewer3d.getMode(ViewMode.PLANE_ROTATION)
            glyph = mode.getGlyph()
            current = getGlyphSize(glyph)
            base_size = self._ui._doubleSpinBoxRotationCentre.value()
            new = [base_size, base_size, base_size]
        elif spin_box == self._ui._doubleSpinBoxSegmentationPoint:
            glyph = self._segmentation_point_glyph
            current = getGlyphSize(glyph)
            base_size = self._ui._doubleSpinBoxSegmentationPoint.value()
            new = [base_size, base_size, base_size]

        if current != new:
            c = CommandSetGlyphSize(current, new, glyph)
            c.setSetGlyphSizeMethod(setGlyphSize)
            c.setSpinBox(spin_box)

            self._model.getUndoRedoStack().push(c)

    def _graphicVisibilityChanged(self):
        check_box = self.sender()
        graphic = None
        if check_box == self._ui._checkBoxCoordinateLabels:
            graphic = self._scene.getGraphic(ELEMENT_NODE_LABEL_GRAPHIC_NAME)
        elif check_box == self._ui._checkBoxImagePlane:
            graphic = self._scene.getGraphic(IMAGE_PLANE_GRAPHIC_NAME)
        elif check_box == self._ui._checkBoxImageOutline:
            graphic = self._scene.getGraphic(ELEMENT_OUTLINE_GRAPHIC_NAME)

        c = CommandSetGraphicVisibility(not check_box.isChecked(), check_box.isChecked())
        c.setCheckBox(check_box)
        c.setGraphic(graphic)

        self._model.getUndoRedoStack().push(c)

    def _streamingCreateClicked(self):
        if self.sender() == self._ui._checkBoxStreamingCreate:
            new = self._ui._checkBoxStreamingCreate.isChecked()
            current = not new

        if current != new:
            c = CommandSetSingleParameterMethod(current, new)
            c.setSingleParameterMethod(self._setStreamingCreate)

            self._model.getUndoRedoStack().push(c)

    def _scaleChanged(self):
        current_scale = self._model.getScale()
        new_scale = current_scale[:]
        line_edit = self.sender()
        if line_edit == self._ui._lineEditWidthScale:
            change_scale_index = 0
            new_scale[0] = float(self._ui._lineEditWidthScale.text())
        elif line_edit == self._ui._lineEditHeightScale:
            change_scale_index = 1
            new_scale[1] = float(self._ui._lineEditHeightScale.text())
        elif line_edit == self._ui._lineEditDepthScale:
            change_scale_index = 2
            new_scale[2] = float(self._ui._lineEditDepthScale.text())

        if new_scale != current_scale:
            c = CommandSetScale(current_scale, new_scale, change_scale_index)
            c.setLineEdit(line_edit)
            c.setSetScaleMethod(self._model.setScale)

            self._model.getUndoRedoStack().push(c)

    def _setStreamingCreate(self, on=True):
        self._streaming_create = on
        self._ui._checkBoxStreamingCreate.setChecked(on)

    def keyPressEvent(self, keyevent):
        if keyevent.key() == 68 and not self._debug_print:
            self._debug_print = True

    def keyReleaseEvent(self, keyevent):
        if keyevent.key() == 82 and keyevent.modifiers() & QtCore.Qt.CTRL and not keyevent.isAutoRepeat():
            # Put tool into plane rotation mode
            # show sphere centre glyph
            return
            reverse = keyevent.modifiers() & QtCore.Qt.SHIFT
            cur_mode = self._ui._sceneviewer3d.getMode().getModeType()
            new_mode = cur_mode
            if cur_mode == ViewMode.SEGMENT:
                if reverse:
                    new_mode = ViewMode.PLANE_ROTATION
                else:
                    new_mode = ViewMode.PLANE_NORMAL
            elif cur_mode == ViewMode.PLANE_NORMAL:
                if reverse:
                    new_mode = ViewMode.SEGMENT
                else:
                    new_mode = ViewMode.PLANE_ROTATION
            elif cur_mode == ViewMode.PLANE_ROTATION:
                if reverse:
                    new_mode = ViewMode.PLANE_NORMAL
                else:
                    new_mode = ViewMode.SEGMENT

            self._setMode(new_mode)

        if keyevent.key() == 68 and not keyevent.isAutoRepeat():
            self._debug_print = False

    def _zincWidgetModeChanged(self):
        if self.sender() == self._ui._radioButtonSegment:
            self._setMode(ViewMode.SEGMENT)
        elif self.sender() == self._ui._radioButtonMove:
            self._setMode(ViewMode.PLANE_NORMAL)
        elif self.sender() == self._ui._radioButtonRotate:
            self._setMode(ViewMode.PLANE_ROTATION)

    def _setMode(self, view_mode):
        c = CommandChangeViewMode(self._current_viewmode, view_mode)
        c.setSetActiveModeTypeMethod(self._ui._sceneviewer3d.setActiveModeType)
        c.setSetViewModeUiMethod(self._setViewModeUi)

        self._model.getUndoRedoStack().push(c)
        self._current_viewmode = view_mode

    def _setupTabs(self):
        self._tabs = {}
        context = self._model.getContext()

        view3d = SceneviewerTab(context, self._model.getUndoRedoStack())
        self._ui._tabWidgetLeft.addTab(view3d, 'View 3D')

        view2d = SceneviewerTab(context, self._model.getUndoRedoStack(), view3d.getZincWidget())
        view2d.setPlane(self._model.getImageModel().getPlane())
        self._ui._tabWidgetLeft.addTab(view2d, 'View 2D')

        self._tabs['view_3d'] = view3d
        self._tabs['view_2d'] = view2d

    def _setupTools(self):
        context = self._model.getContext()
        image_model = self._model.getImageModel()
        node_model = self._model.getNodeModel()
        plane = image_model.getPlane()
        undo_redo_stack = self._model.getUndoRedoStack()

        materialmodule = context.getMaterialmodule()
        yellow_material = materialmodule.findMaterialByName('yellow')
        orange_material = materialmodule.findMaterialByName('orange')
        purple_material = materialmodule.findMaterialByName('purple')
        red_material = materialmodule.findMaterialByName('red')

        view_3d_tab = self._tabs['view_3d']
        segment_tool = segment3d.Segment3D(view_3d_tab.getZincWidget(), plane, undo_redo_stack)
        segment_tool.setModel(node_model)

        normal_tool = normal.Normal(view_3d_tab.getZincWidget(), plane, undo_redo_stack)
        normal_tool.setGetDimensionsMethod(image_model.getDimensions)
        normal_tool.setDefaultMaterial(yellow_material)
        normal_tool.setSelectedMaterial(orange_material)

        rotation_tool = orientation.Orientation(view_3d_tab.getZincWidget(), plane, undo_redo_stack)
        rotation_tool.setGetDimensionsMethod(image_model.getDimensions)
        rotation_tool.setDefaultMaterial(purple_material)
        rotation_tool.setSelectedMaterial(red_material)

        view_3d_tab.addTool(segment_tool)
        view_3d_tab.addTool(normal_tool)
        view_3d_tab.addTool(rotation_tool)

        view_2d_tab = self._tabs['view_2d']
        segment2d_tool = segment2d.Segment2D(view_2d_tab.getZincWidget(), plane, undo_redo_stack)
        segment2d_tool.setGetDimensionsMethod(image_model.getDimensions)
        segment2d_tool.setModel(node_model)

        view_2d_tab.addTool(segment2d_tool)


