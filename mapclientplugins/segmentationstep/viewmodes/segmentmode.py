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
from mapclientplugins.segmentationstep.viewmodes.abstractviewmode import AbstractViewMode
from mapclientplugins.segmentationstep.widgets.definitions import ViewMode

class SegmentMode(AbstractViewMode):

    def __init__(self, plane, undo_redo_stack):
        super(SegmentMode, self).__init__(plane, undo_redo_stack)
        self._mode_type = ViewMode.SEGMENT
        self._getViewParameters_method = None
        self._setViewParameters_method = None
        self._node_picker_method = None

    def setGetViewParametersMethod(self, get_view_parameters_method):
        self._getViewParameters_method = get_view_parameters_method

    def setSetViewParametersMethod(self, set_view_parameters_method):
        self._setViewParameters_method = set_view_parameters_method

    def setNodePickerMethod(self, method):
        self._node_picker_method = method

    def mouseMoveEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()


