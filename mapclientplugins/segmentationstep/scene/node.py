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
from mapclientplugins.segmentationstep.definitions import DEFAULT_SEGMENTATION_POINT_SIZE, POINT_CLOUD_GRAPHIC_NAME, \
    POINT_CLOUD_ON_PLANE_GRAPHIC_NAME

class NodeScene(object):
    '''
    classdocs
    '''


    def __init__(self, model):
        '''
        Constructor
        '''
        self._model = model
        self._setupNodeVisualisation()

    def _setupNodeVisualisation(self):
        region = self._model.getRegion()
        coordinate_field = self._model.getScaledCoordinateField()
        self._segmentation_point_glyph = self._createNodeGraphics(region, coordinate_field)
        self._segmentation_point_on_plane_glyph = self._createNodeOnPlaneGraphics(region, coordinate_field)

    def _createNodeGraphics(self, region, finite_element_field):
        scene = region.getScene()
        scene.beginChange()

        materialmodule = scene.getMaterialmodule()
        green_material = materialmodule.findMaterialByName('green')

        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphic.setCoordinateField(finite_element_field)
        graphic.setName(POINT_CLOUD_GRAPHIC_NAME)
        graphic.setSelectedMaterial(green_material)
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(DEFAULT_SEGMENTATION_POINT_SIZE)

        scene.endChange()

        return graphic

    def _createNodeOnPlaneGraphics(self, region, finite_element_field):
        scene = region.getScene()
        scene.beginChange()

        materialmodule = scene.getMaterialmodule()
        green_material = materialmodule.findMaterialByName('green')

        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphic.setCoordinateField(finite_element_field)
        graphic.setName(POINT_CLOUD_ON_PLANE_GRAPHIC_NAME)
        graphic.setSelectedMaterial(green_material)
        graphic.setSubgroupField(self._model.getPlaneGroupField())
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(DEFAULT_SEGMENTATION_POINT_SIZE)

        scene.endChange()

        return graphic

    def getGraphic(self, name):
        graphic = None
        if name == POINT_CLOUD_GRAPHIC_NAME:
            graphic = self._segmentation_point_glyph
        elif name == POINT_CLOUD_ON_PLANE_GRAPHIC_NAME:
            graphic = self._segmentation_point_on_plane_glyph

        return graphic

