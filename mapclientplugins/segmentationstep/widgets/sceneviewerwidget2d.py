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
# from opencmiss.zinc.field import Field

from mapclientplugins.segmentationstep.widgets.sceneviewerwidget import SceneviewerWidget
from mapclientplugins.segmentationstep.maths.vectorops import add
from mapclientplugins.segmentationstep.widgets.definitions import IMAGE_PLANE_GRAPHIC_NAME

class SceneviewerWidget2D(SceneviewerWidget):

    def __init__(self, parent=None, shared=None):
        super(SceneviewerWidget2D, self).__init__(parent, shared)
        self._plane = None
        self._model = None

    def setModel(self, model):
        self._model = model

    def _setViewParameters(self):
        plane = self._model.getImageModel().getPlane()
        normal = plane.getNormal()
        centre = plane.calculateCentroid()
        _, _, up = self.getViewParameters()
        self.setViewParameters(add(normal, centre), centre, up)

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


