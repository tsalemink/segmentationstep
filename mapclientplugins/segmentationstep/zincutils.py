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
from PySide6 import QtCore

from cmlibs.zinc.sceneviewerinput import Sceneviewerinput
from cmlibs.zinc.field import Field
from cmlibs.zinc.glyph import Glyph
from cmlibs.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_LOCAL, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT
from cmlibs.zinc.graphics import Graphics

from cmlibs.utils.zinc.finiteelement import create_cube_element

COORDINATE_SYSTEM_LOCAL = SCENECOORDINATESYSTEM_LOCAL
COORDINATE_SYSTEM_WINDOW_PIXEL_TOP_LEFT = SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT

from mapclientplugins.segmentationstep.definitions import DEFAULT_GRAPHICS_SPHERE_SIZE, DEFAULT_NORMAL_ARROW_SIZE, \
    PLANE_MANIPULATION_SPHERE_GRAPHIC_NAME, PLANE_MANIPULATION_NORMAL_GRAPHIC_NAME

button_map = {
    QtCore.Qt.MouseButton.LeftButton: Sceneviewerinput.BUTTON_TYPE_LEFT,
    QtCore.Qt.MouseButton.MiddleButton: Sceneviewerinput.BUTTON_TYPE_MIDDLE,
    QtCore.Qt.MouseButton.RightButton: Sceneviewerinput.BUTTON_TYPE_RIGHT
}
# Create a modifier map of Qt modifier keys to Zinc modifier keys
def modifier_map(qt_modifiers):
    '''
    Return a Zinc SceneViewerInput modifiers object that is created from
    the Qt modifier flags passed in.
    '''
    modifiers = Sceneviewerinput.MODIFIER_FLAG_NONE
    if qt_modifiers & QtCore.Qt.KeyboardModifier.ShiftModifier:
        modifiers = modifiers | Sceneviewerinput.MODIFIER_FLAG_SHIFT

    return modifiers

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
    a, b, c = dim
    node_coordinate_set = [[0, 0, 0], [a, 0, 0], [0, b, 0], [a, b, 0], [0, 0, c], [a, 0, c], [0, b, c], [a, b, c]]
    create_cube_element(fieldmodule.findMeshByDimension(3), finite_element_field, node_coordinate_set)

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


