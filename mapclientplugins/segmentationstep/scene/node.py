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

from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.graphics import Graphics

from mapclientplugins.segmentationstep.definitions import DEFAULT_SEGMENTATION_POINT_SIZE, POINT_CLOUD_GRAPHIC_NAME, \
    POINT_CLOUD_ON_PLANE_GRAPHIC_NAME, CURVE_GRAPHIC_NAME, CURVE_ON_PLANE_GRAPHIC_NAME, \
    INTERPOLATION_POINT_GRAPHIC_NAME, INTERPOLATION_POINT_ON_PLANE_GRAPHIC_NAME

class NodeScene(object):

    def __init__(self, model):
        self._model = model
        self._curve_interpolation_graphics = {}
        self._curve_interpolation_on_plane_graphics = {}
        self._setupNodeVisualisation()

    def _setupNodeVisualisation(self):
        region = self._model.getRegion()
        coordinate_field = self._model.getScaledCoordinateField()
        self._segmentation_point_glyph = self._createPointCloudGraphics(region, coordinate_field)
        self._segmentation_point_on_plane_glyph = self._createPointCloudOnPlaneGraphics(region, coordinate_field)
        self._curve_point_glyph = self._createCurveGraphics(region, coordinate_field)
        self._curve_point_on_plane_glyph = self._createCurveOnPlaneGraphics(region, coordinate_field)
        self._interpolation_point_glyph = _createInterpolationPointGraphics(region, coordinate_field)
        self._interpolation_point_on_plane_glyph = self._createInterpolationPointOnPlaneGraphics(region, coordinate_field)

    def _createPointCloudGraphics(self, region, finite_element_field):
        scene = region.getScene()
        scene.beginChange()

        materialmodule = scene.getMaterialmodule()
        green_material = materialmodule.findMaterialByName('green')

        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphic.setCoordinateField(finite_element_field)
        graphic.setName(POINT_CLOUD_GRAPHIC_NAME)
        graphic.setSelectedMaterial(green_material)
        graphic.setSubgroupField(self._model.getPointCloudGroupField())
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(DEFAULT_SEGMENTATION_POINT_SIZE)

        scene.endChange()

        return graphic

    def _createPointCloudOnPlaneGraphics(self, region, finite_element_field):
        scene = region.getScene()
        scene.beginChange()

        materialmodule = scene.getMaterialmodule()
        green_material = materialmodule.findMaterialByName('green')

        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphic.setCoordinateField(finite_element_field)
        graphic.setName(POINT_CLOUD_ON_PLANE_GRAPHIC_NAME)
        graphic.setSelectedMaterial(green_material)
        graphic.setSubgroupField(self._model.getOnPlanePointCloudField())
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(DEFAULT_SEGMENTATION_POINT_SIZE)

        scene.endChange()

        return graphic

    def _createCurveGraphics(self, region, finite_element_field):
        scene = region.getScene()
        scene.beginChange()

        materialmodule = scene.getMaterialmodule()
        yellow_material = materialmodule.findMaterialByName('yellow')
        red_material = materialmodule.findMaterialByName('red')

        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphic.setCoordinateField(finite_element_field)
        graphic.setName(CURVE_GRAPHIC_NAME)
        graphic.setMaterial(yellow_material)
        graphic.setSelectedMaterial(red_material)
        graphic.setSubgroupField(self._model.getCurveGroupField())
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(DEFAULT_SEGMENTATION_POINT_SIZE)

        scene.endChange()

        return graphic

    def _createCurveOnPlaneGraphics(self, region, finite_element_field):
        scene = region.getScene()
        scene.beginChange()

        materialmodule = scene.getMaterialmodule()
        yellow_material = materialmodule.findMaterialByName('yellow')
        red_material = materialmodule.findMaterialByName('red')

        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphic.setCoordinateField(finite_element_field)
        graphic.setName(CURVE_ON_PLANE_GRAPHIC_NAME)
        graphic.setMaterial(yellow_material)
        graphic.setSelectedMaterial(red_material)
        graphic.setSubgroupField(self._model.getOnPlaneCurveField())
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(DEFAULT_SEGMENTATION_POINT_SIZE)

        scene.endChange()

        return graphic

    def _createInterpolationPointOnPlaneGraphics(self, region, finite_element_field):
        scene = region.getScene()
        scene.beginChange()

        materialmodule = scene.getMaterialmodule()
        blue_material = materialmodule.findMaterialByName('blue')

        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        graphic.setCoordinateField(finite_element_field)
        graphic.setName(CURVE_ON_PLANE_GRAPHIC_NAME)
        graphic.setMaterial(blue_material)
        graphic.setSelectMode(Graphics.SELECT_MODE_OFF)
        graphic.setSubgroupField(self._model.getOnPlaneSegmentationPointField())
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(DEFAULT_SEGMENTATION_POINT_SIZE)

        scene.endChange()

        return graphic

    def setInterpolationPoints(self, curve_index, locations):
        region = self._model.getRegion()
        scene = region.getScene()
        scene.beginChange()

        glyphs = self._curve_interpolation_graphics[curve_index] if curve_index in self._curve_interpolation_graphics else []
        index = 0
        for location in locations:
            if index >= len(glyphs):
                glyph = self._model.createDatapoint(location)
                glyphs.append(glyph)
            else:
                self._model.setNodeLocation(glyphs[index], location)

            index += 1

        alive_glyphs = glyphs[:index]
        dead_glyphs = glyphs[index:]
        self._removeGlyphs(dead_glyphs)
        scene.endChange()

        self._curve_interpolation_graphics[curve_index] = alive_glyphs

    def clearAllInterpolationPoints(self):
        for curve_index in self._curve_interpolation_graphics:
            self._removeGlyphs(self._curve_interpolation_graphics[curve_index])

        self._curve_interpolation_graphics = {}

    def clearInterpolationPoints(self, curve_index):
        if curve_index in self._curve_interpolation_graphics:
            self._removeGlyphs(self._curve_interpolation_graphics[curve_index])
            self._curve_interpolation_graphics.pop(curve_index)

    def _removeGlyphs(self, glyphs):
        region = self._model.getRegion()
        scene = region.getScene()
        scene.beginChange()
        for glyph in glyphs:
            self._model.removeDatapoint(glyph)
        scene.endChange()

    def getGraphic(self, name):
        graphic = None
        if name == POINT_CLOUD_GRAPHIC_NAME:
            graphic = self._segmentation_point_glyph
        elif name == POINT_CLOUD_ON_PLANE_GRAPHIC_NAME:
            graphic = self._segmentation_point_on_plane_glyph
        elif name == CURVE_GRAPHIC_NAME:
            graphic = self._curve_point_glyph
        elif name == CURVE_ON_PLANE_GRAPHIC_NAME:
            graphic = self._curve_point_on_plane_glyph
        elif name == INTERPOLATION_POINT_GRAPHIC_NAME:
            graphic = self._interpolation_point_glyph
        elif name == INTERPOLATION_POINT_ON_PLANE_GRAPHIC_NAME:
            graphic = self._interpolation_point_on_plane_glyph

        return graphic


def _createInterpolationPointGraphics(region, finite_element_field):
    scene = region.getScene()
    scene.beginChange()

    materialmodule = scene.getMaterialmodule()
    blue_material = materialmodule.findMaterialByName('blue')

    graphic = scene.createGraphicsPoints()
    graphic.setFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
    graphic.setCoordinateField(finite_element_field)
    graphic.setName(CURVE_GRAPHIC_NAME)
    graphic.setMaterial(blue_material)
    graphic.setSelectMode(Graphics.SELECT_MODE_OFF)
#         graphic.setSubgroupField(self._model.getOnPlaneSegmentationPointField())
    attributes = graphic.getGraphicspointattributes()
    attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
    attributes.setBaseSize(DEFAULT_SEGMENTATION_POINT_SIZE)

    scene.endChange()

    return graphic

