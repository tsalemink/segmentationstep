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
from PySide import QtGui

from opencmiss.zinc.context import Context

from mapclientplugins.segmentationstep.maths.vectorops import elmult
from mapclientplugins.segmentationstep.plane import Plane
from mapclientplugins.segmentationstep.zincutils import createFiniteElementField, createFiniteElement

class SegmentationModel(object):

    def __init__(self):
        self._context = Context('Segmentation')
        self._undoStack = QtGui.QUndoStack()

        self._dimensions_px = [0, 0, 0]

        self.defineStandardMaterials()
        self.defineStandardGlyphs()

        self._setupImageRegion()
        self._setupNodeRegion()

    def _setupImageRegion(self):
        self._image_region = self._context.getDefaultRegion().createChild('image')
        fieldmodule = self._image_region.getFieldmodule()
        fieldmodule.beginChange()
        # Create a representation of the plane.  The plane has a normal, centre point and a
        # point of rotation.
        self._plane = Plane(fieldmodule)
        normal_field = self._plane.getNormalField()
        rotation_point_field = self._plane.getRotationPointField()

        self._image_coordinate_field = createFiniteElementField(self._image_region)
        self._image_scale_field = fieldmodule.createFieldConstant([1.0, 1.0, 1.0])
        self._scaled_image_coordinate_field = self._image_coordinate_field * self._image_scale_field
        createFiniteElement(self._image_region, self._image_coordinate_field, [1.0, 1.0, 1.0])

        self._iso_scalar_field = self._createIsoScalarField(fieldmodule, self._scaled_image_coordinate_field, normal_field, rotation_point_field)
        fieldmodule.endChange()

    def _setupNodeRegion(self):
        self._node_region = self._context.getDefaultRegion().createChild('point_cloud')
        node_coordinate_field = createFiniteElementField(self._node_region)
        fieldmodule = node_coordinate_field.getFieldmodule()
        fieldmodule.beginChange()
        self._scaled_node_coordinate_field = fieldmodule.createFieldConstant([1.0, 1.0, 1.0])
        self._scaled_node_coordinate_field = node_coordinate_field * self._scaled_node_coordinate_field
        fieldmodule.endChange()

    def getContext(self):
        return self._context

    def getPointCloud(self):
        return None

    def undoRedoStack(self):
        return self._undoStack

    def defineStandardGlyphs(self):
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()

    def defineStandardMaterials(self):
        '''
        Helper method to define the standard materials.
        '''
        material_module = self._context.getMaterialmodule()
        material_module.defineStandardMaterials()

    def getPlane(self):
        return self._plane

    def getImageRegion(self):
        return self._image_region

    def getImageCoordinateField(self):
        return self._scaled_image_coordinate_field

    def getNodeRegion(self):
        return self._node_region

    def getNodeCoordinateField(self):
        return self._scaled_node_coordinate_field

    def _createIsoScalarField(self, fieldmodule, finite_element_field, plane_normal_field, point_on_plane_field):
        d = fieldmodule.createFieldDotProduct(plane_normal_field, point_on_plane_field)
        iso_scalar_field = fieldmodule.createFieldDotProduct(finite_element_field, plane_normal_field) - d

        return iso_scalar_field

    def getIsoScalarField(self):
        return self._iso_scalar_field

    def getImageDimensionsInPixels(self):
        return self._dimensions_px

    def setImageDimensionsInPixels(self, dimensions):
        self._dimensions_px = dimensions

    def getImageScale(self):
        fieldmodule = self._image_scale_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, scale = self._image_scale_field.evaluateReal(fieldcache, 3)

        return scale

    def setImageScale(self, scale):
        fieldmodule = self._image_scale_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._image_scale_field.assignReal(fieldcache, scale)
        fieldmodule.endChange()

    def setNodeScale(self, scale):
        fieldmodule = self._scaled_node_coordinate_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._scaled_node_coordinate_field.assignReal(fieldcache, scale)
        fieldmodule.endChange()

    def getDimensions(self):
        '''
        Get the scaled dimensions of the texture block
        '''
        scale = self.getImageScale()
        scaled_dimensions = elmult(self._dimensions_px, scale)
        return scaled_dimensions

    def resizeImageElement(self, dimensions):
        node_coordinate_set = [[0, 0, 0], [dimensions[0], 0, 0], [0, dimensions[1], 0], [dimensions[0], dimensions[1], 0], [0, 0, dimensions[2]], [dimensions[0], 0, dimensions[2]], [0, dimensions[1], dimensions[2]], [dimensions[0], dimensions[1], dimensions[2]]]
        fieldmodule = self._image_region.getFieldmodule()
        fieldmodule.beginChange()
        field_cache = fieldmodule.createFieldcache()
        nodeset = fieldmodule.findNodesetByName('nodes')
        for node_id in range(1, nodeset.getSize() + 1):
            node = nodeset.findNodeByIdentifier(node_id)
            field_cache.setNode(node)
            # Pass in floats as an array
            self._image_coordinate_field.assignReal(field_cache, node_coordinate_set[node_id - 1])

        fieldmodule.endChange()






