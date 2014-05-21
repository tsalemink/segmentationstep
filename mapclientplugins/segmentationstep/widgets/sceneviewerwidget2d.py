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
from mapclientplugins.segmentationstep.widgets.sceneviewerwidgetsegmentation import SceneviewerWidgetSegmentation
from mapclientplugins.segmentationstep.maths.vectorops import add
from mapclientplugins.segmentationstep.widgets.definitions import IMAGE_PLANE_GRAPHIC_NAME

class SceneviewerWidget2D(SceneviewerWidgetSegmentation):

    def __init__(self, parent=None, shared=None):
        super(SceneviewerWidget2D, self).__init__(parent, shared)
        self._plane = None

    def setPlane(self, plane):
        self._plane = plane
        self._plane.notifyChange.addObserver(self._setViewParameters)

    def _setViewParameters(self):
        if self._sceneviewer is not None:
            normal = self._plane.getNormal()
            centre = self._plane.getRotationPoint()
            _, _, up, angle = self.getViewParameters()
            self._sceneviewer.beginChange()
            self.setViewParameters(add(normal, centre), centre, up, angle)
            self.viewAll()
            self._sceneviewer.endChange()

    def _setSceneviewerFilters(self):
        filtermodule = self._context.getScenefiltermodule()
#         node_filter = filtermodule.createScenefilterFieldDomainType(Field.DOMAIN_TYPE_NODES)
        visibility_filter = filtermodule.createScenefilterVisibilityFlags()
        label_filter = filtermodule.createScenefilterGraphicsName(IMAGE_PLANE_GRAPHIC_NAME)
#         label_filter.setInverse(True)

        master_filter = filtermodule.createScenefilterOperatorAnd()
#         master_filter.appendOperand(node_filter)
        master_filter.appendOperand(visibility_filter)
        master_filter.appendOperand(label_filter)

        self._sceneviewer.setScenefilter(master_filter)

    def initializeGL(self):
        super(SceneviewerWidget2D, self).initializeGL()

        self._sceneviewer.setTumbleRate(0.0)
        self._sceneviewer.setTranslationRate(0.0)
        self._setViewParameters()
        self._setSceneviewerFilters()
        self.viewAll()


