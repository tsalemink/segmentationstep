"""
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
"""

from PySide2 import QtGui
from mapclientplugins.segmentationstep.definitions import ViewType
from mapclientplugins.segmentationstep.commands.abstractcommand import AbstractCommand


class ViewAll(AbstractCommand):

    def __init__(self, tabs):
        super().__init__('View All')

        # This needs a proper icon:
        self._icon = QtGui.QIcon(':toolbar_icons/normal.png')

        self._3d_sceneviewer_widget = tabs[ViewType.VIEW_3D].getZincWidget()
        self._2d_sceneviewer_widget = tabs[ViewType.VIEW_2D].getZincWidget()

    def get_function(self, view_type):
        if view_type == "View 3D":
            return self.execute_3d
        else:
            return self.execute_2d

    def execute_3d(self):
        if self._3d_sceneviewer_widget.getSceneviewer() is not None:
            self._3d_sceneviewer_widget.viewAll()

    def execute_2d(self):
        if self._2d_sceneviewer_widget.getSceneviewer() is not None:
            self._2d_sceneviewer_widget.viewAll()
