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

class AbstractModel(object):

    def __init__(self, context):
        self._context = context

        self._region = None
        self._coordinate_field = None
        self._scaled_coordinate_field = None

    def getRegion(self):
        return self._region

    def getCoordinateField(self):
        return self._coordinate_field

    def getScaledCoordinateField(self):
        return self._scaled_coordinate_field

