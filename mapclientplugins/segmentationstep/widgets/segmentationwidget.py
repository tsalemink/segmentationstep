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

from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph

from mapclientplugins.segmentationstep.viewmodes import normalmode, rotationmode, segment2dmode, segmentmode
from mapclientplugins.segmentationstep.widgets.ui_segmentationwidget import Ui_SegmentationWidget
from mapclientplugins.segmentationstep.undoredo import CommandAddNode, CommandChangeViewMode, CommandSetScale, CommandSetSingleParameterMethod, CommandSetGraphicVisibility, CommandSetGlyphSize
from mapclientplugins.segmentationstep.widgets.zincwidget import ProjectionMode
from mapclientplugins.segmentationstep.maths.vectorops import eldiv
from mapclientplugins.segmentationstep.widgets.definitions import DEFAULT_GRAPHICS_SPHERE_SIZE, DEFAULT_NORMAL_ARROW_SIZE, DEFAULT_SEGMENTATION_POINT_SIZE, GRAPHIC_LABEL_NAME, POINT_CLOUD_GRAPHIC_NAME
from mapclientplugins.segmentationstep.widgets.definitions import ViewMode, IMAGE_PLANE_GRAPHIC_NAME
from mapclientplugins.segmentationstep.widgets.segmentationstate import SegmentationState
from mapclientplugins.segmentationstep.zincutils import getGlyphSize, setGlyphSize

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
        self._setupUi()

        self._ui.splitterToolBox.setStretchFactor(0, 0)
        self._ui.splitterToolBox.setStretchFactor(1, 1)

        self._model = model
        self._context = self._model.getContext()
        self._ui._sceneviewer2d.setContext(self._context)
        self._ui._sceneviewer3d.setContext(self._context)
        self._ui._sceneviewer2d.setUndoRedoStack(model.getUndoRedoStack())
        self._ui._sceneviewer3d.setUndoRedoStack(model.getUndoRedoStack())
        self._ui._sceneviewer2d.setPlane(model.getImageModel().getPlane())

        self._setupModes()

        self._maxdim = 100

        self._debug_print = False

        self._timer = QtCore.QTimer()
#         self._timer.timeout.connect(self.falsifyMouseEvents)
#         self._timer.start(1000)
        self._counter = 0

        self._viewstate = None
        self._current_viewmode = ViewMode.SEGMENT if self._ui._radioButtonSegment.isChecked() else (ViewMode.PLANE_NORMAL if self._ui._radioButtonMove.isChecked() else ViewMode.PLANE_ROTATION)

        self._streaming_create = False
        self._streaming_create_active = False

        self._setupImageVisualisation()
        self._setupNodeVisualisation()

        self._makeConnections()

    def _makeConnections(self):
        self._ui._sceneviewer2d.graphicsInitialized.connect(self.sceneviewerReady)
        self._ui._sceneviewer3d.graphicsInitialized.connect(self.sceneviewerReady)
        self._ui._pushButtonReset.clicked.connect(self._resetViewClicked)
        self._ui._pushButtonViewAll.clicked.connect(self._viewAllClicked)

        self._ui._radioButtonSegment.clicked.connect(self._zincWidgetModeChanged)
        self._ui._radioButtonMove.clicked.connect(self._zincWidgetModeChanged)
        self._ui._radioButtonRotate.clicked.connect(self._zincWidgetModeChanged)
        self._ui._radioButtonParallel.clicked.connect(self._projectionModeChanged)
        self._ui._radioButtonPerspective.clicked.connect(self._projectionModeChanged)

        self._ui._lineEditWidthScale.editingFinished.connect(self._scaleChanged)
        self._ui._lineEditHeightScale.editingFinished.connect(self._scaleChanged)
        self._ui._lineEditDepthScale.editingFinished.connect(self._scaleChanged)

        self._ui._doubleSpinBoxNormalArrow.valueChanged.connect(self._iconSizeChanged)
        self._ui._doubleSpinBoxRotationCentre.valueChanged.connect(self._iconSizeChanged)
        self._ui._doubleSpinBoxSegmentationPoint.valueChanged.connect(self._iconSizeChanged)

        self._ui._checkBoxCoordinateLabels.clicked.connect(self._graphicVisibilityChanged)
        self._ui._checkBoxImageOutline.clicked.connect(self._graphicVisibilityChanged)
        self._ui._checkBoxImagePlane.clicked.connect(self._graphicVisibilityChanged)

        self._ui._checkBoxStreamingCreate.clicked.connect(self._streamingCreateClicked)

    def _setupUi(self):
        dbl_validator = QtGui.QDoubleValidator()
        dbl_validator.setBottom(0.0)
        self._ui._lineEditWidthScale.setValidator(dbl_validator)
        self._ui._lineEditHeightScale.setValidator(dbl_validator)
        self._ui._lineEditDepthScale.setValidator(dbl_validator)

        self._ui._doubleSpinBoxNormalArrow.setValue(DEFAULT_NORMAL_ARROW_SIZE)
        self._ui._doubleSpinBoxRotationCentre.setValue(DEFAULT_GRAPHICS_SPHERE_SIZE)
        self._ui._doubleSpinBoxSegmentationPoint.setValue(DEFAULT_SEGMENTATION_POINT_SIZE)

    def _updateImageUI(self):
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

    def _viewAllClicked(self):
        self._ui._sceneviewer3d.viewAll()

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
            graphic = self._coordinate_labels
        elif check_box == self._ui._checkBoxImagePlane:
            graphic = self._plane_image_graphic
        elif check_box == self._ui._checkBoxImageOutline:
            graphic = self._image_outline

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

    def _createImageOutline(self, region, finite_element_field):
        scene = region.getScene()

        scene.beginChange()
        # Create a surface graphic and set it's coordinate field
        # to the finite element coordinate field.
        outline = scene.createGraphicsLines()
        outline.setCoordinateField(finite_element_field)
        scene.endChange()

        return outline

    def _createTextureSurface(self, region, coordinate_field, iso_scalar_field):
        scene = region.getScene()

        fm = region.getFieldmodule()
        xi = fm.findFieldByName('xi')
        scene.beginChange()
        # Create a surface graphic and set it's coordinate field
        # to the finite element coordinate field.
        iso_graphic = scene.createGraphicsContours()
        iso_graphic.setCoordinateField(coordinate_field)
        iso_graphic.setTextureCoordinateField(xi)
        iso_graphic.setIsoscalarField(iso_scalar_field)
        iso_graphic.setListIsovalues(0.0)
        iso_graphic.setName(IMAGE_PLANE_GRAPHIC_NAME)

        scene.endChange()

        return iso_graphic

    def _createNodeLabels(self, region, finite_element_field):
        scene = region.getScene()

        scene.beginChange()

        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphic.setCoordinateField(finite_element_field)
        graphic.setName(GRAPHIC_LABEL_NAME)
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_NONE)
        attributes.setLabelField(finite_element_field)

        scene.endChange()

        return graphic

    def _setupImageVisualisation(self):
        image_model = self._model.getImageModel()
        image_region = image_model.getRegion()
        image_coordinate_field = image_model.getScaledCoordinateField()
        iso_scalar_field = image_model.getIsoScalarField()
        material = image_model.getMaterial()

        self._plane_image_graphic = self._createTextureSurface(image_region, image_coordinate_field, iso_scalar_field)
        self._plane_image_graphic.setMaterial(material)
        self._image_outline = self._createImageOutline(image_region, image_coordinate_field)
        self._coordinate_labels = self._createNodeLabels(image_region, image_coordinate_field)
        self._coordinate_labels.setVisibilityFlag(False)

        self._updateImageUI()

    def _setupNodeVisualisation(self):
        node_model = self._model.getNodeModel()
        region = node_model.getRegion()
        coordinate_field = node_model.getScaledCoordinateField()
        self._segmentation_point_glyph = self._createNodeGraphics(region, coordinate_field)

    def _createNodeGraphics(self, region, finite_element_field):
        scene = region.getScene()
        scene.beginChange()

        materialmodule = self._context.getMaterialmodule()
        green_material = materialmodule.findMaterialByName('green')

        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphic.setCoordinateField(finite_element_field)
        graphic.setName(POINT_CLOUD_GRAPHIC_NAME)
        graphic.setSelectedMaterial(green_material)
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(DEFAULT_SEGMENTATION_POINT_SIZE)
#         attributes.setLabelField(finite_element_field)

        scene.endChange()

        return graphic

    def sceneviewerReady(self):
        if self.sender() == self._ui._sceneviewer3d:
            self._saveViewState()

    def _addNode(self, mouseevent):
        position = self._calcluatePlaneIntersection(mouseevent.x(), mouseevent.y())
        if self._coordinatesInElement(position):
            scale = self._model.getScale()
            unscaled_position = eldiv(position, scale)
            c = CommandAddNode(self._node_fieldmodule, unscaled_position)
            self._undoRedoStack.push(c)

    def keyPressEvent(self, keyevent):
        if keyevent.key() == 68 and not self._debug_print:
            self._debug_print = True

    def keyReleaseEvent(self, keyevent):
        if keyevent.key() == 82 and keyevent.modifiers() & QtCore.Qt.CTRL and not keyevent.isAutoRepeat():
            # Put tool into plane rotation mode
            # show sphere centre glyph
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

    def _setViewModeUi(self, mode):
        if mode == ViewMode.SEGMENT:
            self._ui._radioButtonSegment.setChecked(True)
        elif mode == ViewMode.PLANE_NORMAL:
            self._ui._radioButtonMove.setChecked(True)
        elif mode == ViewMode.PLANE_ROTATION:
            self._ui._radioButtonRotate.setChecked(True)

    def _setMode(self, view_mode):
        c = CommandChangeViewMode(self._current_viewmode, view_mode)
        c.setSetActiveModeTypeMethod(self._ui._sceneviewer3d.setActiveModeType)
        c.setSetViewModeUiMethod(self._setViewModeUi)

        self._model.getUndoRedoStack().push(c)
        self._current_viewmode = view_mode

    def _setupSelectionScenefilters(self):
        filtermodule = self._context.getScenefiltermodule()
        visibility_filter = filtermodule.createScenefilterVisibilityFlags()
        node_filter = filtermodule.createScenefilterFieldDomainType(Field.DOMAIN_TYPE_NODES)
        glyph_filter = filtermodule.createScenefilterFieldDomainType(Field.DOMAIN_TYPE_POINT)
        label_filter = filtermodule.createScenefilterGraphicsName(GRAPHIC_LABEL_NAME)
        label_filter.setInverse(True)

        segmentation_point_filter = filtermodule.createScenefilterOperatorAnd()
        segmentation_point_filter.appendOperand(visibility_filter)
        segmentation_point_filter.appendOperand(node_filter)
        segmentation_point_filter.appendOperand(label_filter)

        plane_glyph_filter = filtermodule.createScenefilterOperatorAnd()
        plane_glyph_filter.appendOperand(visibility_filter)
        plane_glyph_filter.appendOperand(glyph_filter)

        segment_mode = self._modes[ViewMode.SEGMENT]
        segment_mode.setSelectionFilter(segmentation_point_filter)
        segment_mode.setSelectionFilterMethod(self._ui._sceneviewer3d.setSelectionfilter)

        normal_mode = self._modes[ViewMode.PLANE_NORMAL]
        normal_mode.setSelectionFilter(plane_glyph_filter)
        normal_mode.setSelectionFilterMethod(self._ui._sceneviewer3d.setSelectionfilter)

        rotation_mode = self._modes[ViewMode.PLANE_ROTATION]
        rotation_mode.setSelectionFilter(plane_glyph_filter)
        rotation_mode.setSelectionFilterMethod(self.setSelectionfilter)
#         rotation_mode.setSelectionFilterMethod(self._ui._sceneviewer3d.setSelectionfilter)

    def _setupModes(self):
        image_model = self._model.getImageModel()
        node_model = self._model.getNodeModel()
        plane = image_model.getPlane()
        undo_redo_stack = self._model.getUndoRedoStack()

        materialmodule = self._context.getMaterialmodule()
        yellow_material = materialmodule.findMaterialByName('yellow')
        orange_material = materialmodule.findMaterialByName('orange')
        purple_material = materialmodule.findMaterialByName('purple')
        red_material = materialmodule.findMaterialByName('red')

        segment_mode = segmentmode.SegmentMode(plane, undo_redo_stack)
        segment_mode_2d = segment2dmode.SegmentMode2D(plane, undo_redo_stack)
        segment_mode_2d.setGetViewParametersMethod(self._ui._sceneviewer2d.getViewParameters)
        segment_mode_2d.setSetViewParametersMethod(self._ui._sceneviewer2d.setViewParameters)
        segment_mode_2d.setProjectUnProjectMethods(self._ui._sceneviewer2d.project, self._ui._sceneviewer2d.unproject)
        segment_mode_2d.setGetDimensionsMethod(image_model.getDimensions)
        segment_mode_2d.setNodePickerMethod(self._ui._sceneviewer2d.getNearestNode)
        segment_mode_2d.setModel(node_model)

        normal_mode = normalmode.NormalMode(plane, undo_redo_stack)
        normal_mode.setGlyphPickerMethod(self._ui._sceneviewer3d.getNearestGraphicsPoint)
        normal_mode.setGetDimensionsMethod(image_model.getDimensions)
        normal_mode.setProjectUnProjectMethods(self._ui._sceneviewer3d.project, self._ui._sceneviewer3d.unproject)
        normal_mode.setDefaultMaterial(yellow_material)
        normal_mode.setSelectedMaterial(orange_material)

        rotation_mode = rotationmode.RotationMode(plane, undo_redo_stack)
        rotation_mode.setGlyphPickerMethod(self._ui._sceneviewer3d.getNearestGraphicsPoint)
        rotation_mode.setProjectUnProjectMethods(self._ui._sceneviewer3d.project, self._ui._sceneviewer3d.unproject)
        rotation_mode.setGetDimensionsMethod(image_model.getDimensions)
        rotation_mode.setWidthHeightMethods(self._ui._sceneviewer3d.width, self._ui._sceneviewer3d.height)
        rotation_mode.setGetViewParametersMethod(self._ui._sceneviewer3d.getViewParameters)
        rotation_mode.setDefaultMaterial(purple_material)
        rotation_mode.setSelectedMaterial(red_material)

        self._ui._sceneviewer3d.addMode(segment_mode)
        self._ui._sceneviewer3d.addMode(normal_mode)
        self._ui._sceneviewer3d.addMode(rotation_mode)

        self._ui._sceneviewer2d.addMode(segment_mode_2d)

        self._ui._sceneviewer3d.setActiveModeType(ViewMode.SEGMENT)
        self._ui._sceneviewer2d.setActiveModeType(ViewMode.SEGMENT)


