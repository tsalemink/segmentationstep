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
from mapclientplugins.segmentationstep.viewmodes.segmentmode import SegmentMode, SELECTION_BOX_GRAPHIC_NAME_2D, SELECTION_BOX_GRAPHIC_NAME_3D
from mapclientplugins.segmentationstep.zincutils import createSelectionBox

class SegmentMode3D(SegmentMode):

    def __init__(self, sceneviewer, plane, undo_redo_stack):
        super(SegmentMode3D, self).__init__(sceneviewer, plane, undo_redo_stack)
        self._start_position = None
        self._scenviewer_filter = None
        self._sceneviewer_filter_orignal = None
        self._selection_box = createSelectionBox(plane.getRegion(), SELECTION_BOX_GRAPHIC_NAME_3D)

    def _createSceneviewerFilter(self):
        sceneviewer = self._view.getSceneviewer()
        scene = sceneviewer.getScene()
        filtermodule = scene.getScenefiltermodule()

        visibility_filter = filtermodule.createScenefilterVisibilityFlags()
        selection_box_2d_filter = filtermodule.createScenefilterGraphicsName(SELECTION_BOX_GRAPHIC_NAME_2D)
        selection_box_2d_filter.setInverse(True)

        master_filter = filtermodule.createScenefilterOperatorAnd()

        master_filter.appendOperand(visibility_filter)
        master_filter.appendOperand(selection_box_2d_filter)

        return master_filter

    def enter(self):
        super(SegmentMode3D, self).enter()
        sceneviewer = self._view.getSceneviewer()
        self._sceneviewer_filter_orignal = sceneviewer.getScenefilter()
        if self._scenviewer_filter is None:
            self._scenviewer_filter = self._createSceneviewerFilter()
        sceneviewer.setScenefilter(self._scenviewer_filter)

    def leave(self):
        super(SegmentMode3D, self).leave()
        sceneviewer = self._view.getSceneviewer()
        sceneviewer.setScenefilter(self._sceneviewer_filter_orignal)

