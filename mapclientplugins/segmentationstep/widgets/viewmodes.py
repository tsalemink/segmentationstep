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
from math import cos, sin, sqrt, acos, pi, copysign

from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph

from mapclientplugins.segmentationstep.widgets.definitions import ViewMode, DEFAULT_GRAPHICS_SPHERE_SIZE, DEFAULT_NORMAL_ARROW_SIZE
from mapclientplugins.segmentationstep.maths.vectorops import add, mult, cross, dot, sub, normalize, magnitude
from mapclientplugins.segmentationstep.maths.algorithms import calculateCentroid, boundCoordinatesToCuboid, calculateLinePlaneIntersection
from mapclientplugins.segmentationstep.plane import PlaneAttitude
from mapclientplugins.segmentationstep.undoredo import CommandMovePlane, CommandMoveGlyph
from mapclientplugins.segmentationstep.zincutils import getGlyphPosition, setGlyphPosition

class AbstractViewMode(object):


    def __init__(self, plane, undo_redo_stack):
        self._default_material = None
        self._selected_material = None
        self._mode_type = None
        self._plane = plane
        self._undo_redo_stack = undo_redo_stack
        self._project_method = None
        self._unproject_method = None
        self._get_dimension_method = None

    def setProjectUnProjectMethods(self, project_method, unproject_method):
        self._project_method = project_method
        self._unproject_method = unproject_method

    def setGetDimensionsMethod(self, get_dimensions_method):
        self._get_dimension_method = get_dimensions_method

    def leave(self):
        pass

    def enter(self):
        pass

    def hasGlyph(self):
        return hasattr(self, '_glyph')

    def getModeType(self):
        return self._mode_type

    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

class GlyphMode(AbstractViewMode):

    def __init__(self, plane, undo_redo_stack):
        super(GlyphMode, self).__init__(plane, undo_redo_stack)
        self._glyph = None
        self._glyph_picker_method = None
        self._plane_attitude_start = None
        self._plane_attitude_end = None

    def setGlyph(self, glyph):
        self._glyph = glyph

    def getGlyph(self):
        return self._glyph

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

    def setUndoRedoCommand(self, name):
        if self._plane_attitude_start != self._plane_attitude_end:
            self._undo_redo_stack.beginMacro(name)

            c1 = CommandMovePlane(self._plane, self._plane_attitude_start, self._plane_attitude_end)
            self._undo_redo_stack.push(c1)
            c2 = CommandMoveGlyph(self._glyph, self._plane_attitude_start.getPoint(), self._plane_attitude_end.getPoint())
            c2.setGlyphMoveMethod(setGlyphPosition)
            self._undo_redo_stack.push(c2)

            self._undo_redo_stack.endMacro()

    def mousePressEvent(self, event):
        self._previous_mouse_position = [event.x(), event.y()]
        self._plane_attitude_start = PlaneAttitude(self._plane.getRotationPoint(), self._plane.getNormal())
        graphic = self._glyph_picker_method(event.x(), event.y())
        if graphic and graphic.isValid():
            graphic.setMaterial(self._selected_material)

    def mouseReleaseEvent(self, event):
        self._plane_attitude_end = PlaneAttitude(self._plane.getRotationPoint(), self._plane.getNormal())
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            self._glyph.setMaterial(self._default_material)

class RotationMode(GlyphMode):
    '''
    Handle sceneviewer input events when in rotation mode.
    The rotation mode allows the user to re-orient the image
    plane and set the plane point of rotation.
    '''
    def __init__(self, plane, undo_redo_stack):
        super(RotationMode, self).__init__(plane, undo_redo_stack)
        self._mode_type = ViewMode.PLANE_ROTATION
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
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            x = mouseevent.x()
            y = mouseevent.y()
            far_plane_point = self._unproject_method(x, -y, -1.0)
            near_plane_point = self._unproject_method(x, -y, 1.0)
            point_on_plane = calculateLinePlaneIntersection(near_plane_point, far_plane_point, self._plane.getRotationPoint(), self._plane.getNormal())
            if point_on_plane is not None:
                dimensions = self._get_dimension_method()
                centroid = calculateCentroid(self._plane.getRotationPoint(), self._plane.getNormal(), dimensions)
                point_on_plane = boundCoordinatesToCuboid(point_on_plane, centroid, dimensions)
                setGlyphPosition(self._glyph, point_on_plane)
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

                eye, lookat, up, _ = self._getViewParameters_method()

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

    def mouseReleaseEvent(self, mouseevent):
        scene = self._glyph.getScene()
        scene.beginChange()
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            point_on_plane = getGlyphPosition(self._glyph)
            self._plane.setRotationPoint(point_on_plane)

        super(RotationMode, self).mouseReleaseEvent(mouseevent)
        scene.endChange()

        self.setUndoRedoCommand('plane rotation')


    def enter(self):
        scene = self._glyph.getScene()
        scene.beginChange()
        super(RotationMode, self).enter()
        setGlyphPosition(self._glyph, self._plane.getRotationPoint())
        scene.endChange()


class NormalMode(GlyphMode):
    '''
    Handle sceneviewer input events when in normal mode.
    The normal mode allows the user to move the plane in 
    the direction of the normal of the plane.  
    '''
    def __init__(self, plane, undo_redo_stack):
        super(NormalMode, self).__init__(plane, undo_redo_stack)
        self._mode_type = ViewMode.PLANE_NORMAL
        self._glyph = _createPlaneNormalIndicator(plane.getRegion(), plane.getNormalField())

    def enter(self):
        scene = self._glyph.getScene()
        scene.beginChange()
        super(NormalMode, self).enter()
        setGlyphPosition(self._glyph, calculateCentroid(self._plane.getRotationPoint(), self._plane.getNormal(), self._get_dimension_method()))
        scene.endChange()

    def mousePressEvent(self, mouseevent):
        super(NormalMode, self).mousePressEvent(mouseevent)
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            pass
        else:
            mouseevent.ignore()

    def mouseMoveEvent(self, mouseevent):
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            pos = getGlyphPosition(self._glyph)
            screen_pos = self._project_method(pos[0], pos[1], pos[2])
            global_cur_pos = self._unproject_method(mouseevent.x(), -mouseevent.y(), screen_pos[2])
            global_old_pos = self._unproject_method(self._previous_mouse_position[0], -self._previous_mouse_position[1], screen_pos[2])
            global_pos_diff = sub(global_cur_pos, global_old_pos)

            n = self._plane.getNormal()
            proj_n = mult(n, dot(global_pos_diff, n))
            new_pos = add(pos, proj_n)
            scene = self._glyph.getScene()
            scene.beginChange()

            plane_centre = calculateCentroid(new_pos, self._plane.getNormal(), self._get_dimension_method())
            if plane_centre is not None:
                self._plane.setRotationPoint(plane_centre)
                setGlyphPosition(self._glyph, plane_centre)

            scene.endChange()
            self._previous_mouse_position = [mouseevent.x(), mouseevent.y()]
        else:
            mouseevent.ignore()

    def mouseReleaseEvent(self, mouseevent):
        scene = self._glyph.getScene()
        scene.beginChange()
        set_undo_redo_command = False
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            point_on_plane = getGlyphPosition(self._glyph)
            self._plane.setRotationPoint(point_on_plane)
            set_undo_redo_command = True
        else:
            mouseevent.ignore()

        super(NormalMode, self).mouseReleaseEvent(mouseevent)
        scene.endChange()

        if set_undo_redo_command:
            self.setUndoRedoCommand('plane normal')


class SegmentMode(AbstractViewMode):

    def __init__(self, plane, undo_redo_stack):
        super(SegmentMode, self).__init__(plane, undo_redo_stack)
        self._mode_type = ViewMode.SEGMENT
        self._getViewParameters_method = None
        self._setViewParameters_method = None

    def setGetViewParametersMethod(self, get_view_parameters_method):
        self._getViewParameters_method = get_view_parameters_method

    def setSetViewParametersMethod(self, set_view_parameters_method):
        self._setViewParameters_method = set_view_parameters_method

    def mouseMoveEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()


class SegmentMode2D(SegmentMode):

    def __init__(self, plane, undo_redo_stack):
        super(SegmentMode2D, self).__init__(plane, undo_redo_stack)
        self._start_position = None

    def mouseMoveEvent(self, event):
        if self._start_position is not None:
            # v_rot = v*cos(theta)+(wxv)*sin(theta)+w*(w.v)*(1-cos(theta))
            # v is our vector
            # w is the unit vector to rotate around
            # theta is the angle to rotate
            if self._start_position[0] == event.x() and self._start_position[1] == event.y():
                return
            centre_point = calculateCentroid(self._plane.getRotationPoint(), self._plane.getNormal(), self._get_dimension_method())
            centre_widget = self._project_method(centre_point[0], centre_point[1], centre_point[2])
            a = sub(centre_widget, [event.x(), -event.y(), centre_widget[2]])
            b = sub(centre_widget, [self._start_position[0], -self._start_position[1], centre_widget[2]])
            c = dot(a, b)
            d = magnitude(a) * magnitude(b)
            theta = acos(min(c / d, 1.0))
            if theta != 0.0:
                g = cross(a, b)
                lookat, eye, up, angle = self._getViewParameters_method()
                w = normalize(sub(lookat, eye))
                if copysign(1, dot(g, [0, 0, 1])) < 0:
                    theta = -theta
                v = up
                p1 = mult(v, cos(theta))
                p2 = mult(cross(w, v), sin(theta))
                p3a = mult(w, dot(w, v))
                p3 = mult(p3a, 1 - cos(theta))
                v_rot = add(p1, add(p2, p3))
                self._setViewParameters_method(lookat, eye, v_rot, angle)
                self._start_position = [event.x(), event.y()]

        else:
            event.ignore()

    def mousePressEvent(self, event):
        self._start_position = None
        if not event.modifiers():
            self._start_position = [event.x(), event.y()]
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if self._start_position is not None:
            # Do undo redo command
            pass
        else:
            event.ignore()


def _createPlaneManipulationSphere(region):
    scene = region.getScene()

    scene.beginChange()

    # Create transparent purple sphere
    plane_rotation_sphere = scene.createGraphicsPoints()
    plane_rotation_sphere.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
    plane_rotation_sphere.setVisibilityFlag(False)
    fm = region.getFieldmodule()
    zero_field = fm.createFieldConstant([0, 0, 0])
    plane_rotation_sphere.setCoordinateField(zero_field)
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

    scene.endChange()

    return plane_normal_indicator


