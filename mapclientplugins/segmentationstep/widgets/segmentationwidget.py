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

from mapclientplugins.segmentationstep.widgets.ui_segmentationwidget import Ui_SegmentationWidget
from mapclientplugins.segmentationstep.undoredo import CommandAddNode

from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph

from mapclientplugins.segmentationstep.widgets.zincwidget import ProjectionMode
from mapclientplugins.segmentationstep.maths.vectorops import div, eldiv, mult
from mapclientplugins.segmentationstep.widgets.definitions import DEFAULT_GRAPHICS_SPHERE_SIZE, DEFAULT_NORMAL_ARROW_SIZE, DEFAULT_SEGMENTATION_POINT_SIZE, GRAPHIC_LABEL_NAME
from mapclientplugins.segmentationstep.widgets.definitions import PlaneMovementMode, IMAGE_PLANE_GRAPHIC_NAME
from mapclientplugins.segmentationstep.widgets.segmentationstate import SegmentationState

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
        self._ui._sceneviewer2d.setModel(self._model)
        self._ui._sceneviewer3d.setModel(self._model)

        self._maxdim = 100

        self._debug_print = False

        self._timer = QtCore.QTimer()
#         self._timer.timeout.connect(self.falsifyMouseEvents)
#         self._timer.start(1000)
        self._counter = 0

        self._viewstate = None

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
        self._undoStack.clear()

    def _saveViewState(self):
        eye, lookat, up = self._ui._sceneviewer3d.getViewParameters()

        self._viewstate = SegmentationState()
        self._viewstate.setViewParameters(eye, lookat, up)
#         self._viewstate.setPointOnPlane(self._getPointOnPlane())
#         self._viewstate.setPlaneNormal(self._getPlaneNormal())
        self._viewstate.setPlaneRotationMode(self._ui._sceneviewer3d.getMode())
        self._viewstate.setProjectionMode(self._ui._sceneviewer3d.getProjectionMode())
        self._viewstate.setPlaneNormalGlyphBaseSize(self._ui._doubleSpinBoxNormalArrow.value())
        self._viewstate.setPlaneRotationCentreGlyphBaseSize(self._ui._doubleSpinBoxRotationCentre.value())

    def _loadViewState(self):
        eye, lookat, up = self._viewstate.getViewParameters()
        self._ui._sceneviewer3d.setViewParameters(eye, lookat, up)
#         self._setPlaneEquation(self._viewstate.getPlaneNormal(), self._viewstate.getPointOnPlane())
        self._ui._sceneviewer3d.setMode(self._viewstate.getPlaneRotationMode())
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
        if self.sender() == self._ui._radioButtonParallel:
            self._ui._sceneviewer3d.setProjectionMode(ProjectionMode.PARALLEL)
        elif self.sender() == self._ui._radioButtonPerspective:
            self._ui._sceneviewer3d.setProjectionMode(ProjectionMode.PERSPECTIVE)

    def _setProjectionMode(self, mode):
        self._ui._radioButtonParallel.setChecked(mode == ProjectionMode.PARALLEL)
        self._ui._radioButtonPerspective.setChecked(mode == ProjectionMode.PERSPECTIVE)
        self._ui._sceneviewer3d.setProjectionMode(mode)

    def _zincWidgetModeChanged(self):
        if self.sender() == self._ui._radioButtonSegment:
            self._setMode(PlaneMovementMode.POSITION)
        elif self.sender() == self._ui._radioButtonMove:
            self._setMode(PlaneMovementMode.NORMAL)
        elif self.sender() == self._ui._radioButtonRotate:
            self._setMode(PlaneMovementMode.ROTATION)

    def _iconSizeChanged(self):
        if self.sender() == self._ui._doubleSpinBoxNormalArrow:
            self._setPlaneNormalGlyphBaseSize(self._ui._doubleSpinBoxNormalArrow.value())
        elif self.sender() == self._ui._doubleSpinBoxRotationCentre:
            self._setPlaneRotationCentreGlyphBaseSize(self._ui._doubleSpinBoxRotationCentre.value())
        elif self.sender() == self._ui._doubleSpinBoxSegmentationPoint:
            self._setSegmentationPointBaseSize(self._ui._doubleSpinBoxSegmentationPoint.value())

    def _graphicVisibilityChanged(self):
        if self.sender() == self._ui._checkBoxCoordinateLabels:
            self._coordinate_labels.setVisibilityFlag(self._ui._checkBoxCoordinateLabels.isChecked())
        elif self.sender() == self._ui._checkBoxImagePlane:
            self._plane_image_graphic.setVisibilityFlag(self._ui._checkBoxImagePlane.isChecked())
        elif self.sender() == self._ui._checkBoxImageOutline:
            self._image_outline.setVisibilityFlag(self._ui._checkBoxImageOutline.isChecked())

    def _streamingCreateClicked(self):
        if self.sender() == self._ui._checkBoxStreamingCreate:
            self._setStreamingCreate(self._ui._checkBoxStreamingCreate.isChecked())

    def _scaleChanged(self):
        current_scale = self._getScale()
        new_scale = current_scale[:]
        if self.sender() == self._ui._lineEditWidthScale:
            new_scale[0] = float(self._ui._lineEditWidthScale.text())
        elif self.sender() == self._ui._lineEditHeightScale:
            new_scale[1] = float(self._ui._lineEditHeightScale.text())
        elif self.sender() == self._ui._lineEditDepthScale:
            new_scale[2] = float(self._ui._lineEditDepthScale.text())

        if new_scale != current_scale:
            self._setScale(new_scale)

    def _setStreamingCreate(self, on=True):
        self._streaming_create = on

    def _getScale(self):
        return self._model.getScale()

    def _setScale(self, scale):
        self._model.setScale(scale)

    def _createImageOutline(self, region, finite_element_field):
        scene = region.getScene()

        scene.beginChange()
        # Create a surface graphic and set it's coordinate field
        # to the finite element coordinate field.
        outline = scene.createGraphicsLines()
#         finite_element_field = field_module.findFieldByName('coordinates')
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
#         attributes.setBaseSize(1)

#         fieldmodule = region.getFieldmodule()
#         field = fieldmodule.findFieldByName('cmiss_number')
        attributes.setLabelField(finite_element_field)

        scene.endChange()

        return graphic

    def _createTestPoints(self):
        region = self._context.getDefaultRegion()
        materialmodule = self._context.getMaterialmodule()
        green = materialmodule.findMaterialByName('green')
        red = materialmodule.findMaterialByName('red')
        scene = region.getScene()
        scene.beginChange()
        self._test_points = []
        i = 0
        while i < 2:
            tp = scene.createGraphicsPoints()
            tp.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
            if i == 0:
                tp.setMaterial(green)
            else:
                tp.setMaterial(red)
            attr = tp.getGraphicspointattributes()
            attr.setGlyphShapeType(Glyph.SHAPE_TYPE_CUBE_SOLID)
            attr.setBaseSize(1)
            self._test_points.append(tp)
            i += 1
#         self._test_point_1 = scene.createGraphicsPoints()
#         self._test_point_2 = scene.createGraphicsPoints()
#         self._test_point_1.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
#         self._test_point_2.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
        scene.endChange()

    def _createImageScaleField(self, fieldmodule):
        return fieldmodule.createFieldConstant([1.0, 1.0, 1.0])

    def showImages(self):
        print('Am I used???')
        # create a material with the images passed in
        image_model = self._model.getImageModel()
        material = image_model.getMaterial()
        # Set the iso graphic to use the image field, that is set
        # the material to the iso graphic
        self._plane_image_graphic.setMaterial(material)
        # update ui elements that use the image information
        self._updateImageUI()

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

        self._updateImageUI()

    def _setupNodeVisualisation(self):
        node_model = self._model.getNodeModel()
        region = node_model.getRegion()
        coordinate_field = node_model.getScaledCoordinateField()
        self._segmentation_point_glyph = self._createNodeGraphics(region, coordinate_field)

#         self._createTestPoints()

    def _createNodeGraphics(self, region, finite_element_field):
        scene = region.getScene()
        scene.beginChange()

        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphic.setCoordinateField(finite_element_field)
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(DEFAULT_SEGMENTATION_POINT_SIZE)
#         attributes.setLabelField(finite_element_field)

        scene.endChange()

        return graphic

    def sceneviewerReady(self):
        if self.sender() == self._ui._sceneviewer3d:
            self._saveViewState()

    def _boundCoordinatesToElement(self, coords):
        dim = self._model.getDimensions()
        bounded_coords = [ max(min(coords[i], dim[i]), 0.0)  for i in range(len(coords)) ]
        return bounded_coords

    def _coordinatesInElement(self, coords):
        dim = self._model.getDimensions()
        for i in range(len(coords)):
            if not self._checkRange(coords[i], 0.0, dim[i]):
                return False

        return True

    def _setSegmentationPointBaseSize(self, base_size):
        scene = self._segmentation_point_glyph.getScene()
        scene.beginChange()
        attributes = self._segmentation_point_glyph.getGraphicspointattributes()
        _, cur_base_size = attributes.getBaseSize(1)
        _, position = attributes.getGlyphOffset(3)
        true_position = mult(position, cur_base_size)
        attributes.setBaseSize(base_size)
        attributes.setGlyphOffset(div(true_position, base_size))
        scene.endChange()

    def _setPlaneRotationCentreGlyphBaseSize(self, base_size):
        scene = self._plane_rotation_glyph.getScene()
        scene.beginChange()
        attributes = self._plane_rotation_glyph.getGraphicspointattributes()
        _, cur_base_size = attributes.getBaseSize(1)
        _, position = attributes.getGlyphOffset(3)
        true_position = mult(position, cur_base_size)
        attributes.setBaseSize(base_size)
        attributes.setGlyphOffset(div(true_position, base_size))
        scene.endChange()

    def _setPlaneRotationCentreGlyphPosition(self, position):
        scene = self._plane_rotation_glyph.getScene()
        scene.beginChange()
        attributes = self._plane_rotation_glyph.getGraphicspointattributes()
        _, base_size = attributes.getBaseSize(1)
        attributes.setGlyphOffset(div(position, base_size))
        scene.endChange()

    def _getPlaneRotationCentreGlyphPosition(self):
        attributes = self._plane_rotation_glyph.getGraphicspointattributes()
        _, base_size = attributes.getBaseSize(1)
        _, position = attributes.getGlyphOffset(3)

        return mult(position, base_size)

    def _setPlaneNormalGlyphBaseSize(self, base_size):
#         scene = self._plane_normal_glyph.getScene()
#         scene.beginChange()
        attributes = self._plane_normal_glyph.getGraphicspointattributes()
        attributes.setBaseSize([base_size, base_size / 4, base_size / 4])

#     def _setGlyphPosition(self, glyph, position):
#         '''
#         This is synonymous with setting the plane centre.
#         '''
#         position_field = glyph.getCoordinateField()
#         fieldmodule = position_field.getFieldmodule()
#         fieldmodule.beginChange()
#         fieldcache = fieldmodule.createFieldcache()
#         position_field.assignReal(fieldcache, position)
#
#         fieldmodule.endChange()
#
#     def _getPlaneNormalGlyphPosition(self):
#         '''
#         This is synonymous with getting the plane centre.
#         '''
#         position_field = self._plane_normal_glyph.getCoordinateField()
#         fieldmodule = position_field.getFieldmodule()
#         fieldcache = fieldmodule.createFieldcache()
#         _, position = position_field.evaluateReal(fieldcache, 3)
#
#         return position

#             self._ui.zinc_widget.setIgnoreMouseEvents(mode != PlaneMovementMode.NONE)

    def _addNode(self, mouseevent):
        position = self._calcluatePlaneIntersection(mouseevent.x(), mouseevent.y())
        if self._coordinatesInElement(position):
            scale = self._getScale()
            unscaled_position = eldiv(position, scale)
            c = CommandAddNode(self._node_fieldmodule, unscaled_position)
            self._undoStack.push(c)

    def keyPressEvent(self, keyevent):
        if keyevent.key() == 68 and not self._debug_print:
            self._debug_print = True

    def keyReleaseEvent(self, keyevent):
        if keyevent.key() == 82 and keyevent.modifiers() & QtCore.Qt.CTRL and not keyevent.isAutoRepeat():
            # Put tool into plane rotation mode
            # show sphere centre glyph
            reverse = keyevent.modifiers() & QtCore.Qt.SHIFT
            cur_mode = self._ui._sceneviewer3d.getMode()
            new_mode = cur_mode
            if cur_mode == PlaneMovementMode.POSITION:
                if reverse:
                    new_mode = PlaneMovementMode.ROTATION
                else:
                    new_mode = PlaneMovementMode.NORMAL
            elif cur_mode == PlaneMovementMode.NORMAL:
                if reverse:
                    new_mode = PlaneMovementMode.POSITION
                else:
                    new_mode = PlaneMovementMode.ROTATION
            elif cur_mode == PlaneMovementMode.ROTATION:
                if reverse:
                    new_mode = PlaneMovementMode.NORMAL
                else:
                    new_mode = PlaneMovementMode.POSITION

            self._ui._sceneviewer3d.setMode(new_mode)

        if keyevent.key() == 68 and not keyevent.isAutoRepeat():
            self._debug_print = False

