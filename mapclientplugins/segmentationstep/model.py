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

from PySide import QtGui

from opencmiss.zinc.context import Context
from opencmiss.zinc.material import Material
from opencmiss.zinc.status import OK

from mapclientplugins.segmentationstep.maths.algorithms import calculateCentroid
from mapclientplugins.segmentationstep.maths.vectorops import elmult
from mapclientplugins.segmentationstep.plane import Plane
from mapclientplugins.segmentationstep.zincutils import createFiniteElementField, createFiniteElement
from mapclientplugins.segmentationstep.misc import alphanum_key

class AbstractModel(object):

    def __init__(self, context):
        self._context = context

        self._region = None
        self._coordinate_field = None
        self._scaled_coordinate_field = None

    def getRegion(self):
        return self._region

    def getCoordinateField(self):
        return self._coordinate_field

    def getScaledCoordinateField(self):
        return self._scaled_coordinate_field

class ImageModel(AbstractModel):
    '''
    A model of the image region containing a 
    single finite element for viewing an image using 
    an iso surface.
    '''

    def __init__(self, context, dataIn):
        super(ImageModel, self).__init__(context)

        self._dimensions_px = [0, 0, 0]

        self._createImageRegion()
        self._image_field = self._createImageField(dataIn)
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
        class attribute '_plane'.  The plane has a normal, centre point and a
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
        directory = dataIn
        files = os.listdir(directory)
        files.sort(key=alphanum_key)
        for filename in files:
            # We are reading in a file from the local disk so our resource is a file.
            absolute_filename = os.path.join(directory, filename)
            if os.path.isfile(absolute_filename):
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


class NodeModel(AbstractModel):

    def __init__(self, context):
        super(NodeModel, self).__init__(context)
        self._setupNodeRegion()
        self._plane_attitudes = {}
        self._nodes = {}


    def _setupNodeRegion(self):
        self._region = self._context.getDefaultRegion().createChild('point_cloud')
#         scene = self._region.getScene()
        self._coordinate_field = createFiniteElementField(self._region)
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()
        self._scale_field = fieldmodule.createFieldConstant([1.0, 1.0, 1.0])
        self._scaled_coordinate_field = self._coordinate_field * self._scale_field
        self._group = None
        fieldmodule.endChange()

    def setScale(self, scale):
        '''
        Don't call this 'setScale' method directly let the main model do that
        this way we can ensure that the two scale fields have the same
        values.
        '''
        fieldmodule = self._region.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        self._scale_field.assignReal(fieldcache, scale)

    def getSelectionFieldGroup(self):
        return self._selectionGroup

    def getSelectionGroup(self):
        return self._group

    def isSelected(self, node):
        return self._group.containsNode(node)

    def getNodeByIdentifier(self, node_id):
        fieldmodule = self._region.getFieldmodule()
        nodeset = fieldmodule.findNodesetByName('nodes')
        node = nodeset.findNodeByIdentifier(node_id)
        return node

    def getNodePlaneAttitude(self, node_id):
        return self._nodes[node_id]

    def _addId(self, plane_attitude, node_id):
        if plane_attitude in self._plane_attitudes:
            self._plane_attitudes[plane_attitude].append(node_id)
        else:
            self._plane_attitudes[plane_attitude] = [node_id]

    def _removeId(self, plane_attitude, node_id):
        index = self._plane_attitudes[plane_attitude].index(node_id)
        del self._plane_attitudes[plane_attitude][index]
        if len(self._plane_attitudes[plane_attitude]) == 0:
            del self._plane_attitudes[plane_attitude]

    def addNode(self, node_id, location, plane_attitude):
        if node_id is -1:
            node = self._createNodeAtLocation(location)
            node_id = node.getIdentifier()
        self._addId(plane_attitude, node_id)
        self._nodes[node_id] = plane_attitude

        return node_id

    def modifyNode(self, node_id, location, plane_attitude):
#         node_id = node.getIdentifier()
        current_plane_attitude = self._nodes[node_id]
        node = self.getNodeByIdentifier(node_id)
        self.setNodeLocation(node, location)
        if current_plane_attitude != plane_attitude:
            self._removeId(current_plane_attitude, node_id)
            self._addId(plane_attitude, node_id)
            self._nodes[node_id] = plane_attitude

    def removeNode(self, node_id):
        plane_attitude = self._nodes[node_id]
        self._removeId(plane_attitude, node_id)
        del self._nodes[node_id]
        node = self.getNodeByIdentifier(node_id)
        nodeset = node.getNodeset()
        nodeset.destroyNode(node)


    def setNodeLocation(self, node, location):
        fieldmodule = self._region.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        fieldcache.setNode(node)
        self._coordinate_field.assignReal(fieldcache, location)
        fieldmodule.endChange()

    def getNodeLocation(self, node):
        fieldmodule = self._region.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        fieldcache.setNode(node)
        result, location = self._coordinate_field.evaluateReal(fieldcache, 3)
        fieldmodule.endChange()

        if result == OK:
            return location

        return None

    def createNode(self):
        '''
        Create a node with the models coordinate field.
        '''
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()

        nodeset = fieldmodule.findNodesetByName('nodes')
        template = nodeset.createNodetemplate()
        template.defineField(self._coordinate_field)

        scene = self._region.getScene()
        selection_field = scene.getSelectionField()
        if selection_field.isValid():
            selection_group_field = selection_field.castGroup()
        else:
            selection_group_field = fieldmodule.createFieldGroup()
            scene.setSelectionField(selection_group_field)

        nodegroup = selection_group_field.getFieldNodeGroup(nodeset)
        if not nodegroup.isValid():
            nodegroup = selection_group_field.createFieldNodeGroup(nodeset)

        selection_group_field.clear()

        node = nodeset.createNode(-1, template)
        nodegroup = selection_group_field.getFieldNodeGroup(nodeset)
        if not nodegroup.isValid():
            nodegroup = selection_group_field.createFieldNodeGroup(nodeset)

        self._group = nodegroup.getNodesetGroup()
        self._group.addNode(node)

        fieldmodule.endChange()

        return node

    def _createNodeAtLocation(self, location):
        '''
        Creates a node at the given location without
        adding it to the current selection.
        '''
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()

        nodeset = fieldmodule.findNodesetByName('nodes')
        template = nodeset.createNodetemplate()
        template.defineField(self._coordinate_field)
        node = nodeset.createNode(-1, template)
        self.setNodeLocation(node, location)
        fieldmodule.endChange()

        return node

class SegmentationModel(object):

    def __init__(self, dataIn):
        self._context = Context('Segmentation')
        self._undoRedoStack = QtGui.QUndoStack()

        self.defineStandardMaterials()
        self._createModeMaterials()
        self.defineStandardGlyphs()

        self._image_model = ImageModel(self._context, dataIn)
        self._node_model = NodeModel(self._context)

    def getContext(self):
        return self._context

    def getPointCloud(self):
        return None

    def getUndoRedoStack(self):
        return self._undoRedoStack

    def getImageModel(self):
        return self._image_model

    def getNodeModel(self):
        return self._node_model

    def defineStandardGlyphs(self):
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()

    def defineStandardMaterials(self):
        '''
        Helper method to define the standard materials.
        '''
        material_module = self._context.getMaterialmodule()
        material_module.defineStandardMaterials()

    def _createModeMaterials(self):
        '''
        Create the extra mode materials required which are not
        defined by defineStandardMaterials().
        '''
        materialmodule = self._context.getMaterialmodule()

        purple_material = materialmodule.createMaterial()
        purple_material.setName('purple')
        purple_material.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.4, 0.0, 0.6])
        purple_material.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.4, 0.0, 0.6])
        purple_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.4)
        purple_material.setManaged(True)

        red_material = materialmodule.findMaterialByName('red')
        red_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.4)

    def getScale(self):
        '''
        The scale is mirrored in both the image model and node model
        unfortunately, we expect them to be the same so just return
        the value from the image model.
        '''
        return self._image_model.getScale()

    def setScale(self, scale):
        '''
        Have to set the scale in both the image model and 
        node model.  As long as we always use this method
        to set the scale they should always have the same value.
        '''
        self._image_model.setScale(scale)
        self._node_model.setScale(scale)


