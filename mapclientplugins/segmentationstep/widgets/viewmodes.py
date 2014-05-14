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
from opencmiss.zinc.field import Field
from opencmiss.zinc.material import Material
from opencmiss.zinc.glyph import Glyph

from mapclientplugins.segmentationstep.widgets.definitions import PlaneMovementMode, DEFAULT_GRAPHICS_SPHERE_SIZE, DEFAULT_NORMAL_ARROW_SIZE

class ViewMode(object):


    def __init__(self, plane):
        self._default_material = None
        self._selected_material = None
        self._mode = None
        self._plane = plane

    def leave(self):
        pass

    def enter(self):
        pass

    def getMode(self):
        return self._mode

    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

class GlyphMode(ViewMode):

    def __init__(self, plane):
        super(GlyphMode, self).__init__(plane)
        self._glyph = None
        self._glyph_picker_method = None

    def setGlyph(self, glyph):
        self._glyph = glyph

    def setGlyphPickerMethod(self, method):
        self._glyph_picker_method = method

    def setDefaultMaterial(self, material):
        self._default_material = material

    def setSelectedMaterial(self, material):
        self._selected_material = material

    def enter(self):
        self._glyph.setVisibilityFlag(True)
        self._glyph.setMaterial(self._default_material)

    def leave(self):
        self._glyph.setVisibilityFlag(False)

    def mousePressEvent(self, event):
        graphic = self._glyph_picker_method(event.x(), event.y())
        if graphic and graphic.isValid():
            graphic.setMaterial(self._selected_material)

    def mouseReleaseEvent(self, event):
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            self._glyph.setMaterial(self._default_material)

class RotationMode(GlyphMode):
    '''
    Handle sceneviewer input events when in rotation mode.
    The rotation mode allows the user to re-orient the image
    plane and set the plane point of rotation.
    '''
    def __init__(self, plane):
        super(RotationMode, self).__init__(plane)
        self._mode = PlaneMovementMode.ROTATION
        self._glyph = _createPlaneManipulationSphere(plane.getRegion())

    def mouseMoveEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        super(RotationMode, self).mousePressEvent(event)

        event.ignore()

    def mouseReleaseEvent(self, event):
        super(RotationMode, self).mouseReleaseEvent(event)
        event.ignore()


class NormalMode(GlyphMode):
    '''
    Handle sceneviewer input events when in normal mode.
    The normal mode allows the user to move the plane in 
    the direction of the normal of the plane.  
    '''
    def __init__(self, plane):
        super(NormalMode, self).__init__(plane)
        self._mode = PlaneMovementMode.NORMAL
        self._glyph = _createPlaneNormalIndicator(plane.getRegion(), plane.getNormalField())

    def mouseMoveEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        super(NormalMode, self).mousePressEvent(event)
        event.ignore()

    def mouseReleaseEvent(self, event):
        super(NormalMode, self).mouseReleaseEvent(event)
        event.ignore()


class PositionMode(ViewMode):
    '''
    '''
    def __init__(self, plane):
        super(PositionMode, self).__init__(plane)
        self._mode = PlaneMovementMode.POSITION

    def mouseMoveEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()

def _createPlaneManipulationSphere(region):
    scene = region.getScene()

    scene.beginChange()

    # Create transparent purple sphere
    plane_rotation_sphere = scene.createGraphicsPoints()
    plane_rotation_sphere.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
    plane_rotation_sphere.setVisibilityFlag(False)
    tessellation = plane_rotation_sphere.getTessellation()
    tessellation.setCircleDivisions(24)
    plane_rotation_sphere.setTessellation(tessellation)
    attributes = plane_rotation_sphere.getGraphicspointattributes()
    attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
    attributes.setBaseSize(DEFAULT_GRAPHICS_SPHERE_SIZE)

    scene.endChange()

    return plane_rotation_sphere

def _createPlaneNormalIndicator(region, plane_normal_field):
    scene = region.getScene()

    scene.beginChange()
    # Create transparent purple sphere
    plane_normal_indicator = scene.createGraphicsPoints()
    plane_normal_indicator.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
    plane_normal_indicator.setVisibilityFlag(False)

    fm = region.getFieldmodule()
    zero_field = fm.createFieldConstant([0, 0, 0])
    plane_normal_indicator.setCoordinateField(zero_field)

    attributes = plane_normal_indicator.getGraphicspointattributes()
    attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_ARROW_SOLID)
    attributes.setBaseSize([DEFAULT_NORMAL_ARROW_SIZE, DEFAULT_NORMAL_ARROW_SIZE / 4, DEFAULT_NORMAL_ARROW_SIZE / 4])
    attributes.setScaleFactors([0, 0, 0])
    attributes.setOrientationScaleField(plane_normal_field)
#         attributes.setLabelField(zero_field)

    scene.endChange()

    return plane_normal_indicator


