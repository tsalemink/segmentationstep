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

from mapclientplugins.segmentationstep.model.abstractmodel import AbstractModel
from mapclientplugins.segmentationstep.maths.algorithms import calculateCentroid
from mapclientplugins.segmentationstep.maths.vectorops import elmult
from mapclientplugins.segmentationstep.plane import Plane
from mapclientplugins.segmentationstep.zincutils import createFiniteElementField, createFiniteElement
from mapclientplugins.segmentationstep.misc import alphanum_key

class ImageModel(AbstractModel):
    '''
    A model of the image region containing a 
    single finite element for viewing an image using 
    an iso surface.
    '''

    def __init__(self, context):
        super(ImageModel, self).__init__(context)

        self._dimensions_px = [0, 0, 0]

        self._createImageRegion()
        self._image_field = None
        self._material = None
        self._plane = None

    def loadImages(self, dataIn):
        self._image_field = self._createImageField(dataIn)

    def initialize(self):
        self._material = self._createMaterialUsingImageField(self._image_field)
        self._plane = self._createPlane()
        self._setupImageRegion()

    def getPlane(self):
        return self._plane

    def getIsoScalarField(self):
        return self._iso_scalar_field

    def getDimensionsInPixels(self):
        return self._dimensions_px

    def setDimensionsInPixels(self, dimensions):
        self._dimensions_px = dimensions

    def getScale(self):
        fieldmodule = self._scale_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, scale = self._scale_field.evaluateReal(fieldcache, 3)

        return scale

    def setScale(self, scale):
        '''
        Don't call this 'setScale' method directly let the main model do that
        this way we can ensure that the two scale fields have the same
        values.
        '''
        fieldmodule = self._scale_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._scale_field.assignReal(fieldcache, scale)
        fieldmodule.endChange()
        # Do I also need to set the dimensions for the self._plane?
        # I'm going to go with yes.
        plane_centre = calculateCentroid(self._plane.getRotationPoint(), self._plane.getNormal(), elmult(self._dimensions_px, scale))
        self._plane.setRotationPoint(plane_centre)  # (elmult(self._dimensions_px, scale))

    def getDimensions(self):
        '''
        Get the scaled dimensions of the texture block
        '''
        scale = self.getScale()
        scaled_dimensions = elmult(self._dimensions_px, scale)
        return scaled_dimensions

    def getMaterial(self):
        return self._material

    def resizeElement(self, dimensions):
        node_coordinate_set = [[0, 0, 0], [dimensions[0], 0, 0], [0, dimensions[1], 0], [dimensions[0], dimensions[1], 0], [0, 0, dimensions[2]], [dimensions[0], 0, dimensions[2]], [0, dimensions[1], dimensions[2]], [dimensions[0], dimensions[1], dimensions[2]]]
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()
        field_cache = fieldmodule.createFieldcache()
        nodeset = fieldmodule.findNodesetByName('nodes')
        for node_id in range(1, nodeset.getSize() + 1):
            node = nodeset.findNodeByIdentifier(node_id)
            field_cache.setNode(node)
            # Pass in floats as an array
            self._coordinate_field.assignReal(field_cache, node_coordinate_set[node_id - 1])

        fieldmodule.endChange()

    def _createImageRegion(self):
        '''
        Creates a child region of the root region called 'image'.  Stores
        a handle to the region in the class attribute '_region'.
        '''
        self._region = self._context.getDefaultRegion().createChild('image')

    def _createPlane(self):
        '''
        Sets up a number of fields to represent the image plane and stores
        a handle to an object encapsulating these fields in the 
        class attribute '_plane'.  The plane has a normal and a
        point of rotation.
        '''
        fieldmodule = self._region.getFieldmodule()

        fieldmodule.beginChange()
        plane = Plane(fieldmodule)
        plane_centre = calculateCentroid(plane.getRotationPoint(), plane.getNormal(), self._dimensions_px)
        plane.setRotationPoint(plane_centre)  # (elmult(self._dimensions_px, scale))
        fieldmodule.endChange()

        return plane

    def _setupImageRegion(self):
        '''
        Adds a single finite element to the region and keeps a handle to the 
        fields created for the finite element in the following attributes(
        self-documenting names):
            '_coordinate_field'
            '_scale_field'
            '_scaled_coordinate_field'
            '_iso_scalar_field'
        '''
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()

        normal_field = self._plane.getNormalField()
        rotation_point_field = self._plane.getRotationPointField()

        self._coordinate_field = createFiniteElementField(self._region)
        self._scale_field = fieldmodule.createFieldConstant([1.0, 1.0, 1.0])
        self._scaled_coordinate_field = self._coordinate_field * self._scale_field
        createFiniteElement(self._region, self._coordinate_field, self._dimensions_px)

        self._iso_scalar_field = self._createIsoScalarField(fieldmodule, self._scaled_coordinate_field, normal_field, rotation_point_field)
        fieldmodule.endChange()

    def _createIsoScalarField(self, fieldmodule, finite_element_field, plane_normal_field, point_on_plane_field):
        d = fieldmodule.createFieldDotProduct(plane_normal_field, point_on_plane_field)
        iso_scalar_field = fieldmodule.createFieldDotProduct(finite_element_field, plane_normal_field) - d

        return iso_scalar_field

    def _createImageField(self, dataIn):
        '''
        Creates an image field from all the *files* in the given 
        directory, assuming a) that the directory exists and b)
        that there are image files in the directory.  c) the image
        files are sufficiently named so that Zinc can determine
        their format.
        
        Sets the class attribute '_dimensions_px' from the image
        data.
        '''
        fieldmodule = self._region.getFieldmodule()
        image_field = fieldmodule.createFieldImage()
        image_field.setName('image_field')
        image_field.setFilterMode(image_field.FILTER_MODE_LINEAR)

        # Create a stream information object that we can use to read the
        # image file from disk
        stream_information = image_field.createStreaminformationImage()
        # specify depth of texture block i.e. number of images
#        stream_information.setAttributeInteger(stream_information.IMAGE_ATTRIBUTE_, self.number_of_images)

        # Load images onto an invidual texture blocks.
        directory = dataIn.location()
        files = os.listdir(directory)
        files.sort(key=alphanum_key)
        for filename in files:
            # We are reading in a file from the local disk so our resource is a file.
            absolute_filename = os.path.join(directory, filename)
            if os.path.isfile(absolute_filename):
                # SWIG cannot handle unicode strings or rather the Zinc interface
                # files cannot handle unicode strings so we convert them to ascii
                # here.
                if isinstance(absolute_filename, unicode):
                    absolute_filename = absolute_filename.encode('ascii', 'ignore')
                stream_information.createStreamresourceFile(absolute_filename)

        # Actually read in the image file into the image field.
        image_field.read(stream_information)

        self._dimensions_px = image_field.getSizeInPixels(3)[1]
        return image_field

    def _setImageTextureSize(self, size):
        '''
        Required if not using 'xi' for the texture coordinate field.
        '''
        image_field = self._material.getTextureField(1).castImage()
        image_field.setTextureCoordinateSizes(size)

    def _createMaterialUsingImageField(self, image_field):
        ''' 
        Use an image field in a material to create an OpenGL texture.  Returns the
        created material.
        '''
        # create a graphics material from the graphics module, assign it a name
        # and set flag to true
        materials_module = self._context.getMaterialmodule()
        material = materials_module.createMaterial()

        # Create an image field. A temporary xi source field is created for us.
        material.setTextureField(1, image_field)

        return material


