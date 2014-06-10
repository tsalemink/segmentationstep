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
from opencmiss.zinc.material import Material

from mapclientplugins.segmentationstep.model.image import ImageModel
from mapclientplugins.segmentationstep.model.node import NodeModel

class SegmentationModel(object):

    def __init__(self, dataIn):
        self._context = Context('Segmentation')
        self._undo_redo_stack = QtGui.QUndoStack()

        self.defineStandardMaterials()
        self._createModeMaterials()
        self.defineStandardGlyphs()

        self._image_model = ImageModel(self._context, dataIn)
        self._node_model = NodeModel(self._context, self._image_model.getPlane())

    def getContext(self):
        return self._context

    def getPointCloud(self):
        return self._node_model.getPointCloud()

    def getUndoRedoStack(self):
        return self._undo_redo_stack

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


class NodeSelection(object):

    def __init__(self):
        pass


