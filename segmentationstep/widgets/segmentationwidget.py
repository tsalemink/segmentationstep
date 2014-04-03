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
import os
from math import sqrt, acos, pi, sin, cos

from PySide import QtGui, QtCore

from segmentationstep.widgets.ui_segmentationwidget import Ui_SegmentationWidget
from segmentationstep.undoredo import CommandMovePlane, CommandAddNode

from opencmiss.zinc.context import Context
from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.material import Material
from opencmiss.zinc.element import Element, Elementbasis

from segmentationstep.widgets.zincwidget import ProjectionMode
from segmentationstep.math.vectorops import add, cross, div, dot, eldiv, elmult, mult, normalize, sub
from segmentationstep.widgets.definitions import DEFAULT_GRAPHICS_SPHERE_SIZE, DEFAULT_NORMAL_ARROW_SIZE, DEFAULT_SEGMENTATION_POINT_SIZE, GRAPHIC_LABEL_NAME
from segmentationstep.widgets.definitions import PlaneMovementMode
from segmentationstep.widgets.segmentationstate import SegmentationState
from segmentationstep.misc import alphanum_key
from segmentationstep.widgets.plane import PlaneDescription, PlaneMovement, PlaneMovementGlyph
from segmentationstep.math.algorithms import CentroidAlgorithm

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


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        QtGui.QWidget.__init__(self, parent)
        self._ui = Ui_SegmentationWidget()
        self._ui.setupUi(self)
        self._setupUi()

#         self._ui.splitter.setStretchFactor(0, 8)
        self._ui.splitterToolBox.setStretchFactor(1, 2)
        self._ui.splitterSceneviewers.setStretchFactor(1, 66)
#         self._ui.actionButton.setText('Add Point(s)')

        self._context = Context('Segmentation')
        self._ui._sceneviewer2d.setContext(self._context)
        self._ui._sceneviewer3d.setContext(self._context)

        self._image_data_location = ''
        self._dimensions = []
        self._maxdim = 100

        self._debug_print = False

        self._timer = QtCore.QTimer()
#         self._timer.timeout.connect(self.falsifyMouseEvents)
#         self._timer.start(1000)
        self._counter = 0

        self._viewstate = None

        # Set up the states of the plane movement modes
        self._modes = {PlaneMovementMode.NONE: PlaneMovement(PlaneMovementMode.NONE),
                       PlaneMovementMode.NORMAL: PlaneMovementGlyph(PlaneMovementMode.NORMAL),
                       PlaneMovementMode.ROTATION: PlaneMovementGlyph(PlaneMovementMode.ROTATION)}
        self._active_mode = None  # self._modes[PlaneMovementMode.NONE]

        self._streaming_create = False
        self._streaming_create_active = False

        self._undoStack = QtGui.QUndoStack()
        self._ui._sceneviewer2d.setUndoStack(self._undoStack)
        self._ui._sceneviewer3d.setUndoStack(self._undoStack)

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
        self._ui._labelmageWidth.setText(str(self._dimensions[0]) + ' px')
        self._ui._labelmageHeight.setText(str(self._dimensions[1]) + ' px')
        self._ui._labelmageDepth.setText(str(self._dimensions[2]) + ' px')

    def _setPlaneEquation(self, normal, point):
        fieldmodule = self._plane_normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        scene = self._iso_graphic.getScene()
        scene.beginChange()
        self._plane_normal_field.assignReal(fieldcache, normal)
        self._point_on_plane_field.assignReal(fieldcache, point)
        self._setPlaneRotationCentreGlyphPosition(point)
        scene.endChange()

    def _getPlaneNormal(self):
        fieldmodule = self._plane_normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, normal = self._plane_normal_field.evaluateReal(fieldcache, 3)

        return normal

    def _setPlaneNormal(self, normal):
        fieldmodule = self._point_on_plane_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        scene = self._iso_graphic.getScene()
        scene.beginChange()
        self._plane_normal_field.assignReal(fieldcache, normal)
        scene.endChange()

    def _setPointOnPlane(self, point):
        fieldmodule = self._point_on_plane_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        scene = self._iso_graphic.getScene()
        scene.beginChange()
        self._point_on_plane_field.assignReal(fieldcache, point)
        self._setPlaneRotationCentreGlyphPosition(point)
        scene.endChange()

    def _getPointOnPlane(self):
        fieldmodule = self._point_on_plane_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, point = self._point_on_plane_field.evaluateReal(fieldcache, 3)

        return point

    def _resetViewClicked(self):
        self._loadViewState()
        self._undoStack.clear()

    def _saveViewState(self):
        eye, lookat, up = self._ui._sceneviewer3d.getViewParameters()

        self._viewstate = SegmentationState()
        self._viewstate.setViewParameters(eye, lookat, up)
        self._viewstate.setPointOnPlane(self._getPointOnPlane())
        self._viewstate.setPlaneNormal(self._getPlaneNormal())
        self._viewstate.setPlaneRotationMode(self._getMode())
        self._viewstate.setProjectionMode(self._ui._sceneviewer3d.getProjectionMode())
        self._viewstate.setPlaneNormalGlyphBaseSize(self._ui._doubleSpinBoxNormalArrow.value())
        self._viewstate.setPlaneRotationCentreGlyphBaseSize(self._ui._doubleSpinBoxRotationCentre.value())

    def _loadViewState(self):
        eye, lookat, up = self._viewstate.getViewParameters()
        self._ui._sceneviewer3d.setViewParameters(eye, lookat, up)
        self._setPlaneEquation(self._viewstate.getPlaneNormal(), self._viewstate.getPointOnPlane())
        self._setMode(self._viewstate.getPlaneRotationMode())
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
            self._setMode(PlaneMovementMode.NONE)
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
            self._iso_graphic.setVisibilityFlag(self._ui._checkBoxImagePlane.isChecked())
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

    def _getDimensions(self):
        scale = self._getScale()
        scaled_dimensions = elmult(self._dimensions, scale)
        return scaled_dimensions

    def _getScale(self):
        fieldmodule = self._image_scale_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, scale = self._image_scale_field.evaluateReal(fieldcache, 3)

        return scale

    def _setScale(self, scale):
        self._setImageScale(scale)
        self._setNodeScale(scale)
        image_field = self._material.getTextureField(1).castImage()
        scaled_dimensions = elmult(self._dimensions, scale)
        image_field.setTextureCoordinateSizes(scaled_dimensions)
        plane_centre = self._calculatePlaneCentre()
        self._setPlaneNormalGlyphPosition(plane_centre)
        self._setPointOnPlane(plane_centre)

    def _setImageScale(self, scale):
        fieldmodule = self._image_scale_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._image_scale_field.assignReal(fieldcache, scale)
        fieldmodule.endChange()

    def _setNodeScale(self, scale):
        fieldmodule = self._node_scale_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._node_scale_field.assignReal(fieldcache, scale)
        fieldmodule.endChange()

    def _createMaterialUsingImageField(self):
        ''' 
        Use an image field in a material to create an OpenGL texture.  Returns the
        size of the image field in pixels.
        '''
        # create a graphics material from the graphics module, assign it a name
        # and set flag to true
        materials_module = self._context.getMaterialmodule()
        self._material = materials_module.createMaterial()
        self._material.setName('texture_block')
        self._material.setManaged(True)

        # Get a handle to the root _surface_region
        root_region = self._context.getDefaultRegion()

        # The field module allows us to create a field image to
        # store the image data into.
        field_module = root_region.getFieldmodule()

        # Create an image field. A temporary xi source field is created for us.
        image_field = field_module.createFieldImage()
        image_field.setName('image_field')
        image_field.setFilterMode(image_field.FILTER_MODE_LINEAR)

        # Create a stream information object that we can use to read the
        # image file from disk
        stream_information = image_field.createStreaminformationImage()
        # specify depth of texture block i.e. number of images
#        stream_information.setAttributeInteger(stream_information.IMAGE_ATTRIBUTE_, self.number_of_images)

        # Load images onto an invidual texture blocks.
        directory = self._image_data_location
        files = os.listdir(directory)
        files.sort(key=alphanum_key)
        for filename in files:
            # We are reading in a file from the local disk so our resource is a file.
            stream_information.createStreamresourceFile(os.path.join(directory, filename))

        # Actually read in the image file into the image field.
        image_field.read(stream_information)
        self._material.setTextureField(1, image_field)
        self._dimensions = image_field.getSizeInPixels(3)[1]
        image_field.setTextureCoordinateSizes(self._dimensions)

        return self._material

    def _createFiniteElementField(self, region):
        field_module = region.getFieldmodule()
        field_module.beginChange()

        # Create a finite element field with 3 components to represent 3 dimensions
        finite_element_field = field_module.createFieldFiniteElement(3)

        # Set the name of the field
        finite_element_field.setName('coordinates')
        # Set the attribute is managed to 1 so the field module will manage the field for us

        finite_element_field.setManaged(True)
        finite_element_field.setTypeCoordinate(True)
        field_module.endChange()

        return finite_element_field

    def create3DFiniteElement(self, field_module, finite_element_field, node_coordinate_set):
        '''
        Create finite element from a template
        '''
        # Find a special node set named 'cmiss_nodes'
        nodeset = field_module.findNodesetByName('nodes')
        node_template = nodeset.createNodetemplate()

        # Set the finite element coordinate field for the nodes to use
        node_template.defineField(finite_element_field)
        field_cache = field_module.createFieldcache()

        node_identifiers = []
        # Create eight nodes to define a cube finite element
        for node_coordinate in node_coordinate_set:
            node = nodeset.createNode(-1, node_template)
            node_identifiers.append(node.getIdentifier())
            # Set the node coordinates, first set the field cache to use the current node
            field_cache.setNode(node)
            # Pass in floats as an array
            finite_element_field.assignReal(field_cache, node_coordinate)

        # Use a 3D mesh to to create the 3D finite element.
        mesh = field_module.findMeshByDimension(3)
        element_template = mesh.createElementtemplate()
        element_template.setElementShapeType(Element.SHAPE_TYPE_CUBE)
        element_node_count = 8
        element_template.setNumberOfNodes(element_node_count)
        # Specify the dimension and the interpolation function for the element basis function
        linear_basis = field_module.createElementbasis(3, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
        # the indecies of the nodes in the node template we want to use.
        node_indexes = [1, 2, 3, 4, 5, 6, 7, 8]


        # Define a nodally interpolated element field or field component in the
        # element_template
        element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

        for i, node_identifier in enumerate(node_identifiers):
            node = nodeset.findNodeByIdentifier(node_identifier)
            element_template.setNode(i + 1, node)

        mesh.defineElement(-1, element_template)

    def _createFiniteElement(self, region, finite_element_field, dim):
        '''
        Create finite element meshes for each of the images.
        '''
        field_module = region.getFieldmodule()
        field_module.beginChange()
        # Define the coordinates for each 3D element
        node_coordinate_set = [[0, 0, 0], [dim[0], 0, 0], [0, dim[1], 0], [dim[0], dim[1], 0], [0, 0, dim[2]], [dim[0], 0, dim[2]], [0, dim[1], dim[2]], [dim[0], dim[1], dim[2]]]
#         node_coordinate_set = [[-0.5, -0.5, -0.5], [dim[0] + 0.5, -0.5, -0.5], [-0.5, dim[1] + 0.5, -0.5], [dim[0] + 0.5, dim[1] + 0.5, -0.5],
#                                 [-0.5, -0.5, dim[2] + 0.5], [dim[0] + 0.5, -0.5, dim[2] + 0.5], [-0.5, dim[1] + 0.5, dim[2] + 0.5], [dim[0] + 0.5, dim[1] + 0.5, dim[2] + 0.5]]
        self.create3DFiniteElement(field_module, finite_element_field, node_coordinate_set)

        field_module.defineAllFaces()
        field_module.endChange()

    def _createPlaneNormalField(self, fieldmodule):
        plane_normal_field = fieldmodule.createFieldConstant([1, 0, 0])
        return plane_normal_field

    def _createPointOnPlaneField(self, fieldmodule):
        point_on_plane_field = fieldmodule.createFieldConstant([0, 0, 0])
        return point_on_plane_field

    def _createIsoScalarField(self, fieldmodule, finite_element_field, plane_normal_field, point_on_plane_field):
        d = fieldmodule.createFieldDotProduct(plane_normal_field, point_on_plane_field)
        iso_scalar_field = fieldmodule.createFieldDotProduct(finite_element_field, plane_normal_field) - d

        return iso_scalar_field

    def _createImageOutline(self, region, finite_element_field):
        scene = region.getScene()

        scene.beginChange()
        # Create a surface graphic and set it's coordinate field to the finite element coordinate field
        # named coordinates
        outline = scene.createGraphicsLines()
#         finite_element_field = field_module.findFieldByName('coordinates')
        outline.setCoordinateField(finite_element_field)
        scene.endChange()

        return outline

    def _createTextureSurface(self, region, finite_element_field, iso_scalar_field):
        '''
        To visualize the 3D finite element that we have created for each _surface_region, we use a 
        surface graphic then set a _material for that surface to use.
        '''
        scene = region.getScene()

        scene.beginChange()
        # Create a surface graphic and set it's coordinate field to the finite element coordinate field
        # named coordinates
        iso_graphic = scene.createGraphicsContours()
        iso_graphic.setCoordinateField(finite_element_field)
        iso_graphic.setMaterial(self._material)
        iso_graphic.setTextureCoordinateField(finite_element_field)
        # set the yz scalar field to our isosurface
        iso_graphic.setIsoscalarField(iso_scalar_field)
        # define the initial position of the isosurface on the texture block
        iso_graphic.setListIsovalues(0.0)  # Range(1, self.initial_positions[0], self.initial_positions[0])

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

        segment_mode = self._modes[PlaneMovementMode.NONE]
        segment_mode.setSelectionFilter(segmentation_point_filter)
        segment_mode.setSelectionFilterMethod(self._ui._sceneviewer3d.setSelectionfilter)

        normal_mode = self._modes[PlaneMovementMode.NORMAL]
        normal_mode.setSelectionFilter(plane_glyph_filter)
        normal_mode.setSelectionFilterMethod(self._ui._sceneviewer3d.setSelectionfilter)

        rotation_mode = self._modes[PlaneMovementMode.ROTATION]
        rotation_mode.setSelectionFilter(plane_glyph_filter)
        rotation_mode.setSelectionFilterMethod(self._ui._sceneviewer3d.setSelectionfilter)


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

    def _createPlaneManipulationSphere(self, region, finite_element_field):
        scene = region.getScene()

        scene.beginChange()

        # Create transparent purple sphere
        plane_rotation_sphere = scene.createGraphicsPoints()
        plane_rotation_sphere.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
        plane_rotation_sphere.setVisibilityFlag(False)
        tessellation = plane_rotation_sphere.getTessellation()
        tessellation.setCircleDivisions(24)
        plane_rotation_sphere.setTessellation(tessellation)
        attributes = plane_rotation_sphere.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(DEFAULT_GRAPHICS_SPHERE_SIZE)

        scene.endChange()

        return plane_rotation_sphere

    def _createPlaneNormalIndicator(self, region, finite_element_field, plane_normal_field):
        scene = region.getScene()

        scene.beginChange()
        # Create transparent purple sphere
        plane_normal_indicator = scene.createGraphicsPoints()
        plane_normal_indicator.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
        plane_normal_indicator.setVisibilityFlag(False)

        fm = region.getFieldmodule()
        zero_field = fm.createFieldConstant([0, 0, 0])
        plane_normal_indicator.setCoordinateField(zero_field)

        attributes = plane_normal_indicator.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_ARROW_SOLID)
        attributes.setBaseSize([DEFAULT_NORMAL_ARROW_SIZE, DEFAULT_NORMAL_ARROW_SIZE / 4, DEFAULT_NORMAL_ARROW_SIZE / 4])
        attributes.setScaleFactors([0, 0, 0])
        attributes.setOrientationScaleField(plane_normal_field)
#         attributes.setLabelField(zero_field)

        scene.endChange()

        return plane_normal_indicator

    def _setGlyphsForGlyphModes(self, rotation_glyph, normal_glyph):
        normal_mode = self._modes[PlaneMovementMode.NORMAL]
        normal_mode.setGlyph(normal_glyph)
        rotation_mode = self._modes[PlaneMovementMode.ROTATION]
        rotation_mode.setGlyph(rotation_glyph)

    def _setMaterialsForGlyphModes(self):
        '''
        Set the materials for the modes that have glyphs.
        '''
        materialmodule = self._context.getMaterialmodule()
        yellow_material = materialmodule.findMaterialByName('yellow')
        orange_material = materialmodule.findMaterialByName('orange')

        purple_material = materialmodule.createMaterial()
        purple_material.setName('purple')
        purple_material.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.4, 0.0, 0.6])
        purple_material.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.4, 0.0, 0.6])
        purple_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.4)

        red_material = materialmodule.findMaterialByName('red')
        red_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.4)

        normal_mode = self._modes[PlaneMovementMode.NORMAL]
        normal_mode.setDefaultMaterial(yellow_material)
        normal_mode.setActiveMaterial(orange_material)

        rotation_mode = self._modes[PlaneMovementMode.ROTATION]
        rotation_mode.setDefaultMaterial(purple_material)
        rotation_mode.setActiveMaterial(red_material)

    def setImageDirectory(self, imagedir):
        self._image_data_location = imagedir

    def defineStandardGlyphs(self):
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()

    def defineStandardMaterials(self):
        '''
        Helper method to define the standard materials.
        '''
        material_module = self._context.getMaterialmodule()
        material_module.defineStandardMaterials()

    def showImages(self):
        self.defineStandardMaterials()
        self.defineStandardGlyphs()
        self._setMaterialsForGlyphModes()
        self._createMaterialUsingImageField()
        self._updateImageUI()
        region = self._context.getDefaultRegion().createChild('image')

        finite_element_field = self._createFiniteElementField(region)
        self._createFiniteElement(region, finite_element_field, self._dimensions)

        fieldmodule = region.getFieldmodule()
        self._image_scale_field = fieldmodule.createFieldConstant([1.0, 1.0, 1.0])
        scaled_finite_element_field = finite_element_field * self._image_scale_field

        self._plane_normal_field = self._createPlaneNormalField(fieldmodule)
        self._point_on_plane_field = self._createPointOnPlaneField(fieldmodule)
        iso_scalar_field = self._createIsoScalarField(fieldmodule, scaled_finite_element_field, self._plane_normal_field, self._point_on_plane_field)
        self._iso_graphic = self._createTextureSurface(region, scaled_finite_element_field, iso_scalar_field)
        self._image_outline = self._createImageOutline(region, scaled_finite_element_field)
        self._coordinate_labels = self._createNodeLabels(region, scaled_finite_element_field)
        self._plane_rotation_glyph = self._createPlaneManipulationSphere(region, scaled_finite_element_field)
        self._plane_normal_glyph = self._createPlaneNormalIndicator(region, scaled_finite_element_field, self._plane_normal_field)
        self._setGlyphsForGlyphModes(self._plane_rotation_glyph, self._plane_normal_glyph)
        plane_centre = self._calculatePlaneCentre()
        self._setPlaneNormalGlyphPosition(plane_centre)
        self._setPointOnPlane(plane_centre)

        region = self._context.getDefaultRegion().createChild('nodes')
        finite_element_field = self._createFiniteElementField(region)
        self._node_fieldmodule = finite_element_field.getFieldmodule()
        self._node_scale_field = self._node_fieldmodule.createFieldConstant([1.0, 1.0, 1.0])
        scaled_finite_element_field = finite_element_field * self._node_scale_field
        self._segmentation_point_glyph = self._createNodeGraphics(region, scaled_finite_element_field)

        self._setupSelectionScenefilters()

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
            self._setMode(PlaneMovementMode.NONE)
            self._saveViewState()

    def _checkRange(self, value, bound1, bound2):
        '''
        Check whether the value 'value' lies within the range 'bound1' and 'bound2'.
        Irrespective of the order of the bounds!
        '''
        check = False
        if bound1 < bound2:
            if bound1 <= value <= bound2:
                check = True
        else:
            if bound2 <= value <= bound1:
                check = True

        return check

    def _calculatePlaneCentre(self):
        tol = 1e-08
        dim = self._getDimensions()  # self._dimensions
        plane_normal = self._getPlaneNormal()
        point_on_plane = self._getPointOnPlane()
        axes = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        coordinate_set = [[0, 0, 0], [dim[0], 0, 0], [0, dim[1], 0], [dim[0], dim[1], 0], [0, 0, dim[2]], [dim[0], 0, dim[2]], [0, dim[1], dim[2]], [dim[0], dim[1], dim[2]]]

        ipts = []
        for axis in axes:
            den = dot(axis, plane_normal)
            if abs(den) < tol:
                continue

            for corner in coordinate_set:
                num = dot(sub(point_on_plane, corner), plane_normal)
                d = num / den

                ipt = add(mult(axis, d), corner)
                # check if all intersections are valid, taking care to be aware of minus signs.
                ipt_0 = self._checkRange(ipt[0], 0.0, dim[0])
                ipt_1 = self._checkRange(ipt[1], 0.0, dim[1])
                ipt_2 = self._checkRange(ipt[2], 0.0, dim[2])

                if ipt_0 and ipt_1 and ipt_2:
                    ipts.append(ipt)

        unique_ipts = []
        for p in ipts:
            insert = True
            for u in unique_ipts:
                vdiff = sub(p, u)
                if sqrt(dot(vdiff, vdiff)) < tol:
                    insert = False
            if insert:
                unique_ipts.append(p)

        if self._debug_print:
            print
            print(ipts)
            print(unique_ipts)

        ca = CentroidAlgorithm(unique_ipts)
#         wa = WeiszfeldsAlgorithm(unique_ipts)
        plane_centre = ca.compute()
        return plane_centre

    def _boundCoordinatesToElement(self, coords):
        dim = self._getDimensions()
        bounded_coords = [ max(min(coords[i], dim[i]), 0.0)  for i in range(len(coords)) ]
        return bounded_coords

    def _coordinatesInElement(self, coords):
        dim = self._getDimensions()
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

    def _setPlaneNormalGlyphPosition(self, position):
        '''
        This is synonymous with setting the plane centre.
        '''
        scene = self._plane_normal_glyph.getScene()
        scene.beginChange()
#         attributes = self._plane_normal_glyph.getGraphicspointattributes()
        position_field = self._plane_normal_glyph.getCoordinateField()
        fieldmodule = position_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        position_field.assignReal(fieldcache, position)

        scene.endChange()

    def _getPlaneNormalGlyphPosition(self):
        '''
        This is synonymous with getting the plane centre.
        '''
        position_field = self._plane_normal_glyph.getCoordinateField()
        fieldmodule = position_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, position = position_field.evaluateReal(fieldcache, 3)

        return position

    def _getMode(self):
        if not self._active_mode is None:
            return self._active_mode.mode()

        return None

    def _setMode(self, mode):
        if mode != self._getMode():
            if not self._active_mode is None:
                self._active_mode.leave()
            self._active_mode = self._modes[mode]
            self._active_mode.enter()

#             self._ui.zinc_widget.setIgnoreMouseEvents(mode != PlaneMovementMode.NONE)

    def _addNode(self, mouseevent):
        position = self._calcluatePlaneIntersection(mouseevent.x(), mouseevent.y())
        if self._coordinatesInElement(position):
            scale = self._getScale()
            unscaled_position = eldiv(position, scale)
            c = CommandAddNode(self._node_fieldmodule, unscaled_position)
            self._undoStack.push(c)

    def _calcluatePlaneIntersection(self, x, y):
        point_on_plane = self._getPointOnPlane()  # self._plane_centre_position  # self._getPointOnPlane()
        plane_normal = self._getPlaneNormal()

        x, y = self._ui._sceneviewer3d.mapToWidget(x, y)
        far_plane_point = self._ui._sceneviewer3d.unproject(x, -y, -1.0)
        near_plane_point = self._ui._sceneviewer3d.unproject(x, -y, 1.0)
        line_direction = sub(near_plane_point, far_plane_point)
        d = dot(sub(point_on_plane, far_plane_point), plane_normal) / dot(line_direction, plane_normal)
        intersection_point = add(mult(line_direction, d), far_plane_point)
        if abs(dot(sub(point_on_plane, intersection_point), plane_normal)) < 1e-08:
            return intersection_point

        return None

    def keyPressEvent(self, keyevent):
        if keyevent.key() == 68 and not self._debug_print:
            self._debug_print = True

    def keyReleaseEvent(self, keyevent):
        if keyevent.key() == 82 and keyevent.modifiers() & QtCore.Qt.CTRL and not keyevent.isAutoRepeat():
            # Put tool into plane rotation mode
            # show sphere centre glyph
            reverse = keyevent.modifiers() & QtCore.Qt.SHIFT
            cur_mode = self._getMode()
            if cur_mode == PlaneMovementMode.NONE:
                if reverse:
                    self._setMode(PlaneMovementMode.ROTATION)
                else:
                    self._setMode(PlaneMovementMode.NORMAL)
            elif cur_mode == PlaneMovementMode.NORMAL:
                if reverse:
                    self._setMode(PlaneMovementMode.NONE)
                else:
                    self._setMode(PlaneMovementMode.ROTATION)
            elif cur_mode == PlaneMovementMode.ROTATION:
                if reverse:
                    self._setMode(PlaneMovementMode.NORMAL)
                else:
                    self._setMode(PlaneMovementMode.NONE)

        if keyevent.key() == 68 and not keyevent.isAutoRepeat():
            self._debug_print = False

    def _startPlaneMovement(self, movement_type):
        pass

    def _performPlaneMovement(self, movement_type):
        pass

    def _endPlaneMovement(self, movement_type):
        pass

    def mousePressEvent(self, mouseevent):
        self._previous_mouse_position = None
        self._start_plane = None
        cur_mode = self._getMode()
        if cur_mode != PlaneMovementMode.NONE:
            self._plane_rotation_mode_graphic = self._ui._sceneviewer3d.getNearestGraphicsPoint(mouseevent.x(), mouseevent.y())
            if self._plane_rotation_mode_graphic:
                self._active_mode.setActive()

            self._previous_mouse_position = [mouseevent.x(), mouseevent.y()]

            if not self._active_mode.isActive() and cur_mode == PlaneMovementMode.NORMAL:
                self._ui._sceneviewer3d.processZincMousePressEvent(mouseevent)
            else:
                self._start_plane = PlaneDescription(self._getPointOnPlane(), self._getPlaneNormal(), self._getPlaneNormalGlyphPosition())

        elif mouseevent.modifiers() & QtCore.Qt.CTRL and mouseevent.button() == QtCore.Qt.LeftButton:
            # If node already at this location then select it and get ready to move it.
            # otherwise add it and set streaming create mode if appropriate.
            self._addNode(mouseevent)
            if self._streaming_create:
                self._streaming_create_active = True

    def mouseMoveEvent(self, mouseevent):
        cur_mode = self._getMode()
        is_active = self._active_mode.isActive()
        if is_active and cur_mode == PlaneMovementMode.ROTATION:
            new_plane_centre = self._calcluatePlaneIntersection(mouseevent.x(), mouseevent.y())
            if not new_plane_centre is None:
                new_plane_centre = self._boundCoordinatesToElement(new_plane_centre)
                self._setPointOnPlane(new_plane_centre)

        elif not is_active and cur_mode == PlaneMovementMode.ROTATION:
            width = self._ui._sceneviewer3d.width()
            height = self._ui._sceneviewer3d.height()
            radius = min([width, height]) / 2.0
            delta_x = float(mouseevent.x() - self._previous_mouse_position[0])
            delta_y = float(mouseevent.y() - self._previous_mouse_position[1])
            tangent_dist = sqrt((delta_x * delta_x + delta_y * delta_y))
            if tangent_dist > 0.0:
                dx = -delta_y / tangent_dist;
                dy = delta_x / tangent_dist;

                d = dx * (mouseevent.x() - 0.5 * (width - 1)) + dy * ((mouseevent.y() - 0.5 * (height - 1)))
                if d > radius: d = radius
                if d < -radius: d = -radius

                phi = acos(d / radius) - 0.5 * pi
                angle = 1.0 * tangent_dist / radius

                eye, lookat, up = self._ui._sceneviewer3d.getViewParameters()

                b = up[:]
                b = normalize(b)
                a = sub(lookat, eye)
                a = normalize(a)
                c = cross(b, a)
                c = normalize(c)
                e = [None, None, None]
                e[0] = dx * c[0] + dy * b[0]
                e[1] = dx * c[1] + dy * b[1]
                e[2] = dx * c[2] + dy * b[2]
                axis = [None, None, None]
                axis[0] = sin(phi) * a[0] + cos(phi) * e[0]
                axis[1] = sin(phi) * a[1] + cos(phi) * e[1]
                axis[2] = sin(phi) * a[2] + cos(phi) * e[2]

                plane_normal = self._getPlaneNormal()
                point_on_plane = self._getPlaneRotationCentreGlyphPosition()

                plane_normal_prime_1 = mult(plane_normal, cos(angle))
                plane_normal_prime_2 = mult(plane_normal, dot(plane_normal, axis) * (1 - cos(angle)))
                plane_normal_prime_3 = mult(cross(axis, plane_normal), sin(angle))
                plane_normal_prime = add(add(plane_normal_prime_1, plane_normal_prime_2), plane_normal_prime_3)

                self._setPlaneEquation(plane_normal_prime, point_on_plane)

                self._previous_mouse_position = [mouseevent.x(), mouseevent.y()]
        elif is_active and cur_mode == PlaneMovementMode.NORMAL:
            pos = self._getPlaneNormalGlyphPosition()  # self._plane_centre_position  # self._getPointOnPlane()
            screen_pos = self._ui._sceneviewer3d.project(pos[0], pos[1], pos[2])
            global_cur_pos = self._ui._sceneviewer3d.unproject(mouseevent.x(), -mouseevent.y(), screen_pos[2])
            global_old_pos = self._ui._sceneviewer3d.unproject(self._previous_mouse_position[0], -self._previous_mouse_position[1], screen_pos[2])
            global_pos_diff = sub(global_cur_pos, global_old_pos)

            n = self._getPlaneNormal()
            proj_n = mult(n, dot(global_pos_diff, n))
            new_pos = add(pos, proj_n)
            scene = self._iso_graphic.getScene()
            scene.beginChange()
            self._setPointOnPlane(new_pos)
            plane_centre = self._calculatePlaneCentre()
            if plane_centre is None:
                self._setPointOnPlane(pos)
            else:
                self._setPlaneNormalGlyphPosition(plane_centre)
                self._setPointOnPlane(plane_centre)

            scene.endChange()
            self._previous_mouse_position = [mouseevent.x(), mouseevent.y()]
        elif not is_active and cur_mode == PlaneMovementMode.NORMAL:
            self._ui._sceneviewer3d.processZincMouseMoveEvent(mouseevent)
        elif self._streaming_create_active:
            self._addNode(mouseevent)

    def mouseReleaseEvent(self, mouseevent):
        c = None
        cur_mode = self._getMode()
        is_active = self._active_mode.isActive()
        if not is_active and cur_mode == PlaneMovementMode.ROTATION:
            plane_centre = self._calculatePlaneCentre()
            if not plane_centre is None:
                self._setPlaneNormalGlyphPosition(plane_centre)

        end_plane = PlaneDescription(self._getPointOnPlane(), self._getPlaneNormal(), self._getPlaneNormalGlyphPosition())
        if is_active:
            self._active_mode.setActive(False)

            c = CommandMovePlane(self._start_plane, end_plane)
        elif cur_mode == PlaneMovementMode.NORMAL:
            self._ui._sceneviewer3d.processZincMouseReleaseEvent(mouseevent)
        elif not self._start_plane is None:
            c = CommandMovePlane(self._start_plane, end_plane)

        if self._streaming_create:
            self._streaming_create_active = False

        if not c is None:
            c.setMethodCallbacks(self._setPlaneNormalGlyphPosition, self._setPlaneEquation)
            self._undoStack.push(c)

    def undoRedoStack(self):
        return self._undoStack

    def getPointCloud(self):
        return self._ui._sceneviewer3d.getPointCloud()

