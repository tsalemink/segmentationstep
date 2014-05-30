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

from mapclientplugins.segmentationstep.widgets.definitions import ELEMENT_NODE_LABEL_GRAPHIC_NAME, IMAGE_PLANE_GRAPHIC_NAME, ELEMENT_OUTLINE_GRAPHIC_NAME

class ImageScene(object):
    '''
    classdocs
    '''


    def __init__(self, model):
        '''
        Constructor
        '''
        self._model = model
        self._setupImageVisualisation()

    def _createImageOutline(self, region, finite_element_field):
        scene = region.getScene()

        scene.beginChange()
        # Create a surface graphic and set it's coordinate field
        # to the finite element coordinate field.
        outline = scene.createGraphicsLines()
        outline.setCoordinateField(finite_element_field)
        outline.setName(ELEMENT_OUTLINE_GRAPHIC_NAME)
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
        graphic.setName(ELEMENT_NODE_LABEL_GRAPHIC_NAME)
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_NONE)
        attributes.setLabelField(finite_element_field)

        scene.endChange()

        return graphic

    def _setupImageVisualisation(self):
        image_region = self._model.getRegion()
        image_coordinate_field = self._model.getScaledCoordinateField()
        iso_scalar_field = self._model.getIsoScalarField()
        material = self._model.getMaterial()

        self._plane_image_graphic = self._createTextureSurface(image_region, image_coordinate_field, iso_scalar_field)
        self._plane_image_graphic.setMaterial(material)
        self._image_outline = self._createImageOutline(image_region, image_coordinate_field)
        self._coordinate_labels = self._createNodeLabels(image_region, image_coordinate_field)
        self._coordinate_labels.setVisibilityFlag(False)

    def getGraphic(self, name):
        graphic = None
        if name == ELEMENT_NODE_LABEL_GRAPHIC_NAME:
            graphic = self._coordinate_labels
        elif name == IMAGE_PLANE_GRAPHIC_NAME:
            graphic = self._plane_image_graphic
        elif name == ELEMENT_OUTLINE_GRAPHIC_NAME:
            graphic = self._image_outline

        return graphic

