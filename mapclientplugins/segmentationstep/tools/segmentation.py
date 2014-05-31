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

class SegmentationTool(object):
    '''
    classdocs
    '''


    def __init__(self, name, undo_redo_stack):
        '''
        Constructor
        '''
        self._name = name
        self._icon = None
        self._handlers = {}
        self._widget = None
        self._undo_redo_stack = undo_redo_stack

    def getName(self):
        return self._name

    def getPropertiesWidget(self):
        raise self._widget

    def getIcon(self):
        return self._icon

    def getHandler(self, view_type):
        return self._handlers[view_type]

    def setGetDimensionsMethod(self, get_dimensions_method):
        pass

    def setDefaultMaterial(self, material):
        pass

    def setSelectedMaterial(self, material):
        pass

    def setModel(self, model):
        pass


