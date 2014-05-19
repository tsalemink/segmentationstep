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
from math import cos, sin, sqrt, acos, pi

from opencmiss.zinc.status import OK
from opencmiss.zinc.field import Field
# from opencmiss.zinc.material import Material
from opencmiss.zinc.glyph import Glyph

from mapclientplugins.segmentationstep.widgets.definitions import PlaneMovementMode, DEFAULT_GRAPHICS_SPHERE_SIZE, DEFAULT_NORMAL_ARROW_SIZE
from mapclientplugins.segmentationstep.maths.vectorops import eldiv, add, mult, cross, dot, sub, normalize, elmult

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

    def hasGlyph(self):
        return hasattr(self, '_glyph')

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
        self._plane = plane
        self._glyph = None
        self._glyph_picker_method = None
        self._project_method = None
        self._unproject_method = None

    def setGlyph(self, glyph):
        self._glyph = glyph

    def setGlyphPickerMethod(self, method):
        self._glyph_picker_method = method

    def setProjectUnProjectMethods(self, project_method, unproject_method):
        self._project_method = project_method
        self._unproject_method = unproject_method

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
        self._previous_mouse_position = [event.x(), event.y()]
#         self._start_plane = PlaneAttitude(self._getPointOnPlane(), self._getPlaneNormal(), self._getPlaneNormalGlyphPosition())
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
        self._width_method = None
        self._height_method = None
        self._getViewParameters_method = None

    def setWidthHeightMethods(self, width_method, height_method):
        self._width_method = width_method
        self._height_method = height_method

    def setGetViewParametersMethod(self, get_view_parameters_method):
        self._getViewParameters_method = get_view_parameters_method

    def mousePressEvent(self, mouseevent):
        super(RotationMode, self).mousePressEvent(mouseevent)

    def mouseMoveEvent(self, mouseevent):
        scene = self._glyph.getScene()
        scene.beginChange()
        super(RotationMode, self).mouseMoveEvent(mouseevent)
#         event.ignore()
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            x = mouseevent.x()
            y = mouseevent.y()
            far_plane_point = self._unproject_method(x, -y, -1.0)
            near_plane_point = self._unproject_method(x, -y, 1.0)
            point_on_plane = self._plane.calcluateIntersection(near_plane_point, far_plane_point)
            if not point_on_plane is None:
#                 point_on_plane = self._plane.boundCoordinatesToElement(point_on_plane)
#                 self._plane.setRotationPoint(point_on_plane)
                _setGlyphPosition(self._glyph, point_on_plane)
#                 print('valid plane centre', point_on_plane)
        else:
            width = self._width_method()
            height = self._height_method()
            radius = min([width, height]) / 2.0
            delta_x = float(mouseevent.x() - self._previous_mouse_position[0])
            delta_y = float(mouseevent.y() - self._previous_mouse_position[1])
            tangent_dist = sqrt((delta_x * delta_x + delta_y * delta_y))
            if tangent_dist > 0.0:
                dx = -delta_y / tangent_dist;
                dy = delta_x / tangent_dist;

                d = dx * (mouseevent.x() - 0.5 * (width - 1)) + dy * ((mouseevent.y() - 0.5 * (height - 1)))
                if d > radius: d = radius
                if d < -radius: d = -radius

                phi = acos(d / radius) - 0.5 * pi
                angle = 1.0 * tangent_dist / radius

                eye, lookat, up = self._getViewParameters_method()

                b = up[:]
                b = normalize(b)
                a = sub(lookat, eye)
                a = normalize(a)
                c = cross(b, a)
                c = normalize(c)
                e = [None, None, None]
                e[0] = dx * c[0] + dy * b[0]
                e[1] = dx * c[1] + dy * b[1]
                e[2] = dx * c[2] + dy * b[2]
                axis = [None, None, None]
                axis[0] = sin(phi) * a[0] + cos(phi) * e[0]
                axis[1] = sin(phi) * a[1] + cos(phi) * e[1]
                axis[2] = sin(phi) * a[2] + cos(phi) * e[2]

                plane_normal = self._plane.getNormal()
                point_on_plane = self._plane.getRotationPoint()

                plane_normal_prime_1 = mult(plane_normal, cos(angle))
                plane_normal_prime_2 = mult(plane_normal, dot(plane_normal, axis) * (1 - cos(angle)))
                plane_normal_prime_3 = mult(cross(axis, plane_normal), sin(angle))
                plane_normal_prime = add(add(plane_normal_prime_1, plane_normal_prime_2), plane_normal_prime_3)

                self._plane.setPlaneEquation(plane_normal_prime, point_on_plane)

                self._previous_mouse_position = [mouseevent.x(), mouseevent.y()]
        scene.endChange()

    def mouseReleaseEvent(self, event):
        scene = self._glyph.getScene()
        scene.beginChange()
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            point_on_plane = _getGlyphPosition(self._glyph)
            self._plane.setRotationPoint(point_on_plane)

        super(RotationMode, self).mouseReleaseEvent(event)
        scene.endChange()
#                 self._plane.setRotationPoint(point_on_plane)
#         event.ignore()

    def enter(self):
        scene = self._glyph.getScene()
        scene.beginChange()
        super(RotationMode, self).enter()
        _setGlyphPosition(self._glyph, self._plane.getRotationPoint())
        scene.endChange()


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

    def enter(self):
        scene = self._glyph.getScene()
        scene.beginChange()
        super(NormalMode, self).enter()
        _setGlyphPosition(self._glyph, self._plane.calculateCentroid())
        scene.endChange()

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
#     attributes.setOrientationScaleField(plane_normal_field)

    scene.endChange()

    return plane_normal_indicator

def _setGlyphPosition(glyph, position):
    '''
    Sets the glyph position taking into account 
    the glyphs basesize, doesn't use scene 
    beginChange, endChange do this outside of 
    this function.
    '''
    attributes = glyph.getGraphicspointattributes()
    result, base_size = attributes.getBaseSize(3)
    if result == OK and position is not None:
        attributes.setGlyphOffset(eldiv(position, base_size))

def _getGlyphPosition(glyph):
    '''
    Gets the glyph position taking into account 
    the glyphs basesize, doesn't use scene 
    beginChange, endChange do this outside of 
    this function.
    '''
    attributes = glyph.getGraphicspointattributes()
    _, base_size = attributes.getBaseSize(3)
    _, position = attributes.getGlyphOffset(3)

    return elmult(position, base_size)
#     if result == OK and position is not None:
#         attributes.setGlyphOffset(eldiv(position, base_size))


