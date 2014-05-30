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
from mapclientplugins.segmentationstep.widgets.definitions import ELEMENT_NODE_LABEL_GRAPHIC_NAME, IMAGE_PLANE_GRAPHIC_NAME, ELEMENT_OUTLINE_GRAPHIC_NAME
from mapclientplugins.segmentationstep.scene.image import ImageScene
from mapclientplugins.segmentationstep.scene.node import NodeScene

class MasterScene(object):
    '''
    classdocs
    '''


    def __init__(self, model):
        '''
        Constructor
        '''
        self._model = model
        self._image = ImageScene(model.getImageModel())
        self._node = NodeScene(model.getNodeModel())

    def getImageScene(self):
        return self._image

    def getNodeScene(self):
        return self._node

    def getGraphic(self, name):
        if name == ELEMENT_NODE_LABEL_GRAPHIC_NAME or name == IMAGE_PLANE_GRAPHIC_NAME or name == ELEMENT_OUTLINE_GRAPHIC_NAME:
            return self._image.getGraphic(name)

        return None


