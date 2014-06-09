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
class SegmentPointStatus(object):

    def __init__(self, node_id, location, plane_attitude):
        self._node_identifier = node_id
        self._location = location
        self._plane_attitude = plane_attitude

    def getNodeIdentifier(self):
        return self._node_identifier

    def setNodeIdentifier(self, identifier):
        self._node_identifier = identifier

    def getLocation(self):
        return self._location

    def setLocation(self, location):
        self._location = location

    def getPlaneAttitude(self):
        return self._plane_attitude

    def setPlaneAttitude(self, plane_attitude):
        self._plane_attitude = plane_attitude


class ControlPointStatus(SegmentPointStatus):

    def __init__(self, node_id, location, plane_attitude):
        super(ControlPointStatus, self).__init__(node_id, location, plane_attitude)
        self._curve_index = None

    def setCurveIndex(self, index):
        self._curve_index = index

    def getCurveIndex(self):
        return self._curve_index


