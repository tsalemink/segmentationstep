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
from PySide2 import QtCore

from opencmiss.zinc.sceneviewerinput import Sceneviewerinput
from opencmiss.zinc.element import Element, Elementbasis
from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_LOCAL, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT
from opencmiss.zinc.graphics import Graphics

COORDINATE_SYSTEM_LOCAL = SCENECOORDINATESYSTEM_LOCAL
COORDINATE_SYSTEM_WINDOW_PIXEL_TOP_LEFT = SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT

from mapclientplugins.segmentationstep.definitions import DEFAULT_GRAPHICS_SPHERE_SIZE, DEFAULT_NORMAL_ARROW_SIZE, \
    PLANE_MANIPULATION_SPHERE_GRAPHIC_NAME, PLANE_MANIPULATION_NORMAL_GRAPHIC_NAME

button_map = {QtCore.Qt.LeftButton: Sceneviewerinput.BUTTON_TYPE_LEFT, QtCore.Qt.MidButton: Sceneviewerinput.BUTTON_TYPE_MIDDLE, QtCore.Qt.RightButton: Sceneviewerinput.BUTTON_TYPE_RIGHT}
# Create a modifier map of Qt modifier keys to Zinc modifier keys
def modifier_map(qt_modifiers):
    '''
    Return a Zinc SceneViewerInput modifiers object that is created from
    the Qt modifier flags passed in.
    '''
    modifiers = Sceneviewerinput.MODIFIER_FLAG_NONE
    if qt_modifiers & QtCore.Qt.SHIFT:
        modifiers = modifiers | Sceneviewerinput.MODIFIER_FLAG_SHIFT

    return modifiers

def createFiniteElementField(region):
    '''
    Create a finite element field of three dimensions
    called 'coordinates' and set the coordinate type true.
    '''
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

def create1DFiniteElement(finite_element_field, node1, node2):
    # Use a 3D mesh to to create the 3D finite element.
    fieldmodule = finite_element_field.getFieldmodule()
    mesh = fieldmodule.findMeshByDimension(1)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_LINE)
    element_node_count = 2
    element_template.setNumberOfNodes(element_node_count)
    # Specify the dimension and the interpolation function for the element basis function
    linear_basis = fieldmodule.createElementbasis(1, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    # the indecies of the nodes in the node template we want to use.
    node_indexes = [1, 2]

    # Define a nodally interpolated element field or field component in the
    # element_template
    element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)
    element_template.setNode(1, node1)
    element_template.setNode(2, node2)

    element = mesh.createElement(-1, element_template)

    return element

def create3DFiniteElement(fieldmodule, finite_element_field, node_coordinate_set):
    '''
    Create a single finite element using the supplied 
    finite element field and node coordinate set.
    '''
    # Find a special node set named 'nodes'
    nodeset = fieldmodule.findNodesetByName('nodes')
    node_template = nodeset.createNodetemplate()

    # Set the finite element coordinate field for the nodes to use
    node_template.defineField(finite_element_field)
    field_cache = fieldmodule.createFieldcache()

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
    mesh = fieldmodule.findMeshByDimension(3)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_CUBE)
    element_node_count = 8
    element_template.setNumberOfNodes(element_node_count)
    # Specify the dimension and the interpolation function for the element basis function
    linear_basis = fieldmodule.createElementbasis(3, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    # the indecies of the nodes in the node template we want to use.
    node_indexes = [1, 2, 3, 4, 5, 6, 7, 8]


    # Define a nodally interpolated element field or field component in the
    # element_template
    element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

    for i, node_identifier in enumerate(node_identifiers):
        node = nodeset.findNodeByIdentifier(node_identifier)
        element_template.setNode(i + 1, node)

    mesh.defineElement(-1, element_template)

def createFiniteElement(region, finite_element_field, dim):
    '''
    Create finite element meshes using the supplied
    finite element field (of three dimensions) and dim list
    of size 3.  The dimension list is the maximum value for a 
    particular dimension.  The origin of the element is set
    at [0, 0, 0].
    '''
    fieldmodule = region.getFieldmodule()
    fieldmodule.beginChange()
    # Define the coordinates for each 3D element
    node_coordinate_set = [[0, 0, 0], [dim[0], 0, 0], [0, dim[1], 0], [dim[0], dim[1], 0], [0, 0, dim[2]], [dim[0], 0, dim[2]], [0, dim[1], dim[2]], [dim[0], dim[1], dim[2]]]
#         node_coordinate_set = [[-0.5, -0.5, -0.5], [dim[0] + 0.5, -0.5, -0.5], [-0.5, dim[1] + 0.5, -0.5], [dim[0] + 0.5, dim[1] + 0.5, -0.5],
#                                 [-0.5, -0.5, dim[2] + 0.5], [dim[0] + 0.5, -0.5, dim[2] + 0.5], [-0.5, dim[1] + 0.5, dim[2] + 0.5], [dim[0] + 0.5, dim[1] + 0.5, dim[2] + 0.5]]
    create3DFiniteElement(fieldmodule, finite_element_field, node_coordinate_set)

    fieldmodule.defineAllFaces()
    fieldmodule.endChange()

def setGlyphPosition(glyph, position):
    if position is not None:
        position_field = glyph.getCoordinateField()
        fieldmodule = position_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        position_field.assignReal(fieldcache, position)

def getGlyphPosition(glyph):
    position_field = glyph.getCoordinateField()
    fieldmodule = position_field.getFieldmodule()
    fieldcache = fieldmodule.createFieldcache()
    _, position = position_field.evaluateReal(fieldcache, 3)

    return position

def getGlyphSize(glyph):
    attributes = glyph.getGraphicspointattributes()
    _, base_size = attributes.getBaseSize(3)
    return base_size

def setGlyphSize(glyph, size):
    attributes = glyph.getGraphicspointattributes()
    attributes.setBaseSize(size)

def setGlyphOffset(glyph, offset):
    attributes = glyph.getGraphicspointattributes()
    attributes.setGlyphOffset(offset)

def createSelectionBox(region, name):
    scene = region.getScene()
    fm = region.getFieldmodule()
    zero_field = fm.createFieldConstant([0, 0, 0])

    scene.beginChange()
    selection_box = scene.createGraphicsPoints()
    selection_box.setName(name)
    selection_box.setCoordinateField(zero_field)
    selection_box.setScenecoordinatesystem(SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT)
    attributes = selection_box.getGraphicspointattributes()
    attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_CUBE_WIREFRAME)
    attributes.setBaseSize([10, 10, 0.9999])

    selection_box.setVisibilityFlag(False)
    scene.endChange()

    return selection_box

def createPlaneManipulationSphere(region):
    scene = region.getScene()

    scene.beginChange()

    # Create transparent purple sphere
    plane_rotation_sphere = scene.createGraphicsPoints()
    plane_rotation_sphere.setName(PLANE_MANIPULATION_SPHERE_GRAPHIC_NAME)
    plane_rotation_sphere.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
    plane_rotation_sphere.setVisibilityFlag(False)
    fm = region.getFieldmodule()
    zero_field = fm.createFieldConstant([0, 0, 0])
    plane_rotation_sphere.setCoordinateField(zero_field)
    tessellation = plane_rotation_sphere.getTessellation()
    tessellation.setCircleDivisions(24)
    plane_rotation_sphere.setTessellation(tessellation)
    attributes = plane_rotation_sphere.getGraphicspointattributes()
    attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
    attributes.setBaseSize(DEFAULT_GRAPHICS_SPHERE_SIZE)

    scene.endChange()

    return plane_rotation_sphere

def createPlaneNormalIndicator(region, plane_normal_field):
    scene = region.getScene()

    scene.beginChange()
    # Create transparent purple sphere
    plane_normal_indicator = scene.createGraphicsPoints()
    plane_normal_indicator.setName(PLANE_MANIPULATION_NORMAL_GRAPHIC_NAME)
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

    scene.endChange()

    return plane_normal_indicator

def createInterpolationPointAtLocation(region, name, size, location, subgroupfield=None):
    scene = region.getScene()

    materialmodule = scene.getMaterialmodule()
    blue_material = materialmodule.findMaterialByName('blue')

    fm = region.getFieldmodule()
    zero_field = fm.createFieldConstant(location)
    graphic = scene.createGraphicsPoints()
    graphic.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
    graphic.setName(name)
    graphic.setMaterial(blue_material)
    graphic.setCoordinateField(zero_field)
    graphic.setSelectMode(Graphics.SELECT_MODE_OFF)
    if subgroupfield is not None:
        graphic.setSubgroupField(subgroupfield)
    attributes = graphic.getGraphicspointattributes()
    attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
    attributes.setBaseSize(size)

    return graphic


