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
class AbstractViewMode(object):


    def __init__(self, plane, undo_redo_stack):
        self._mode_type = None
        self._plane = plane
        self._undo_redo_stack = undo_redo_stack
        self._project_method = None
        self._unproject_method = None
        self._get_dimension_method = None

    def setProjectUnProjectMethods(self, project_method, unproject_method):
        self._project_method = project_method
        self._unproject_method = unproject_method

    def setGetDimensionsMethod(self, get_dimensions_method):
        self._get_dimension_method = get_dimensions_method

    def leave(self):
        pass

    def enter(self):
        pass

    def hasGlyph(self):
        return hasattr(self, '_glyph')

    def getModeType(self):
        return self._mode_type

    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

