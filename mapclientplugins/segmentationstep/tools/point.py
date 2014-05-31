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

from mapclientplugins.segmentationstep.definitions import ViewType
from mapclientplugins.segmentationstep.tools.segmentation import SegmentationTool
from mapclientplugins.segmentationstep.tools.handlers.point2d import Point2D
from mapclientplugins.segmentationstep.tools.handlers.point3d import Point3D

class PointTool(SegmentationTool):

    def __init__(self, plane, undo_redo_stack):
        super(PointTool, self).__init__('Point', undo_redo_stack)
        self._icon = QtGui.QIcon(':/toolbar_icons/point.png')
        self._handlers[ViewType.VIEW_2D] = Point2D(plane, undo_redo_stack)
        self._handlers[ViewType.VIEW_3D] = Point3D(plane, undo_redo_stack)

    def setGetDimensionsMethod(self, get_dimensions_method):
        self._handlers[ViewType.VIEW_2D].setGetDimensionsMethod(get_dimensions_method)


