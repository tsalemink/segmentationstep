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

from segmentationstep.widgets.definitions import PlaneMovementMode

class PlaneMovement(object):

    def __init__(self, mode=PlaneMovementMode.NONE):
        self._mode = mode
        self._active = False
        self._selectionfilter = None
        self._set_selection_filter_method = None

    def isActive(self):
        return self._active

    def mode(self):
        return self._mode

    def setSelectionFilter(self, selectionfilter):
        self._selectionfilter = selectionfilter

    def setSelectionFilterMethod(self, selectionfilter_method):
        self._set_selection_filter_method = selectionfilter_method

    def leave(self):
        pass

    def enter(self):
        if self._set_selection_filter_method and self._selectionfilter:
            self._set_selection_filter_method(self._selectionfilter)


class PlaneMovementGlyph(PlaneMovement):

    def __init__(self, mode):
        super(PlaneMovementGlyph, self).__init__(mode)
        self._default_material = None
        self._active_material = None
        self._glyph = None

    def setDefaultMaterial(self, material):
        self._default_material = material

    def setActiveMaterial(self, material):
        self._active_material = material

    def setActive(self, active=True):
        self._active = active
        if self._glyph and active:
            self._glyph.setMaterial(self._active_material)
        elif self._glyph and not active:
            self._glyph.setMaterial(self._default_material)

    def setGlyph(self, glyph):
        self._glyph = glyph

    def enter(self):
        super(PlaneMovementGlyph, self).enter()
        self.setActive(False)
        self._glyph.setVisibilityFlag(True)

    def leave(self):
        super(PlaneMovementGlyph, self).leave()
        self.setActive(False)
        self._glyph.setVisibilityFlag(False)


class PlaneDescription(object):

    def __init__(self, point, normal, centre):
        self._point = point
        self._normal = normal
        self._centre = centre

    def getPoint(self):
        return self._point

    def getNormal(self):
        return self._normal

    def getCentre(self):
        return self._centre


