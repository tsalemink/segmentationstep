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
from math import sqrt, acos, pi, sin, cos

from PySide import QtCore

from opencmiss.zinc.field import Field
from opencmiss.zinc.material import Material
from opencmiss.zinc.glyph import Glyph

from mapclientplugins.segmentationstep.maths.vectorops import add, cross, dot, mult, normalize, sub
from mapclientplugins.segmentationstep.widgets.sceneviewerwidget import SceneviewerWidget
from mapclientplugins.segmentationstep.widgets.definitions import PlaneMovementMode
from mapclientplugins.segmentationstep.undoredo import CommandMovePlane
from mapclientplugins.segmentationstep.widgets.definitions import GRAPHIC_LABEL_NAME

from mapclientplugins.segmentationstep.widgets.viewmodes import NormalMode, RotationMode, PositionMode

class SceneviewerWidget3D(SceneviewerWidget):

    def __init__(self, parent=None, shared=None):
        super(SceneviewerWidget3D, self).__init__(parent, shared)

        self._active_mode = None
        self._modes = None
        self._plane = None

    def initializeGL(self):
        super(SceneviewerWidget3D, self).initializeGL()

        # Set the initial state for the view
        self._active_mode = self._modes[PlaneMovementMode.POSITION]

    def _setupModes(self, model):
        plane = model.getPlane()

        purple_material, red_material, yellow_material, orange_material = self._createModeMaterials()

        position_mode = PositionMode(plane)

        normal_mode = NormalMode(plane)
        normal_mode.setGlyphPickerMethod(self.getNearestGraphicsPoint)
        normal_mode.setGetDimensionsMethod(model.getDimensions)
        normal_mode.setDefaultMaterial(yellow_material)
        normal_mode.setSelectedMaterial(orange_material)

        rotation_mode = RotationMode(plane)
        rotation_mode.setGlyphPickerMethod(self.getNearestGraphicsPoint)
        rotation_mode.setProjectUnProjectMethods(self.project, self.unproject)
        rotation_mode.setGetDimensionsMethod(model.getDimensions)
        rotation_mode.setWidthHeightMethods(self.width, self.height)
        rotation_mode.setGetViewParametersMethod(self.getViewParameters)
        rotation_mode.setDefaultMaterial(purple_material)
        rotation_mode.setSelectedMaterial(red_material)

        self._modes = {PlaneMovementMode.POSITION: position_mode,
                       PlaneMovementMode.NORMAL: normal_mode,
                       PlaneMovementMode.ROTATION: rotation_mode}

    def _setupUi(self):
        print('Am I actually used')
        self._setGlyphsForGlyphModes(self._rotation_glyph, self._normal_glyph)
        self._setMaterialsForGlyphModes()

    def setModel(self, model):
        self._model = model
        self._setupModes(self._model.getImageModel())

    def getPlaneNormalGlyph(self):
        return self._normal_glyph

    def getPlaneRotationGlyph(self):
        return self._rotation_glyph

    def getMode(self):
        if not self._active_mode is None:
            return self._active_mode.getMode()

        return None

    def setMode(self, mode):
        if mode != self._active_mode.getMode():
            if not self._active_mode is None:
                self._active_mode.leave()
            self._active_mode = self._modes[mode]
            self._active_mode.enter()

    def _createModeMaterials(self):
        materialmodule = self._context.getMaterialmodule()
        yellow_material = materialmodule.findMaterialByName('yellow')
        orange_material = materialmodule.findMaterialByName('orange')

        purple_material = materialmodule.createMaterial()
        purple_material.setName('purple')
        purple_material.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.4, 0.0, 0.6])
        purple_material.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.4, 0.0, 0.6])
        purple_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.4)

        red_material = materialmodule.findMaterialByName('red')
        red_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.4)

        return purple_material, red_material, yellow_material, orange_material

    def _setupSelectionScenefilters(self):
        filtermodule = self._context.getScenefiltermodule()
        visibility_filter = filtermodule.createScenefilterVisibilityFlags()
        node_filter = filtermodule.createScenefilterFieldDomainType(Field.DOMAIN_TYPE_NODES)
        glyph_filter = filtermodule.createScenefilterFieldDomainType(Field.DOMAIN_TYPE_POINT)
        label_filter = filtermodule.createScenefilterGraphicsName(GRAPHIC_LABEL_NAME)
        label_filter.setInverse(True)

        segmentation_point_filter = filtermodule.createScenefilterOperatorAnd()
        segmentation_point_filter.appendOperand(visibility_filter)
        segmentation_point_filter.appendOperand(node_filter)
        segmentation_point_filter.appendOperand(label_filter)

        plane_glyph_filter = filtermodule.createScenefilterOperatorAnd()
        plane_glyph_filter.appendOperand(visibility_filter)
        plane_glyph_filter.appendOperand(glyph_filter)

        segment_mode = self._modes[PlaneMovementMode.POSITION]
        segment_mode.setSelectionFilter(segmentation_point_filter)
        segment_mode.setSelectionFilterMethod(self._ui._sceneviewer3d.setSelectionfilter)

        normal_mode = self._modes[PlaneMovementMode.NORMAL]
        normal_mode.setSelectionFilter(plane_glyph_filter)
        normal_mode.setSelectionFilterMethod(self._ui._sceneviewer3d.setSelectionfilter)

        rotation_mode = self._modes[PlaneMovementMode.ROTATION]
        rotation_mode.setSelectionFilter(plane_glyph_filter)
        rotation_mode.setSelectionFilterMethod(self._ui._sceneviewer3d.setSelectionfilter)

    def mousePressEvent(self, mouseevent):
        self._active_mode.mousePressEvent(mouseevent)
        if not mouseevent.isAccepted():
            super(SceneviewerWidget3D, self).mousePressEvent(mouseevent)
#         self._previous_mouse_position = None
#         self._start_plane = None
#         cur_mode = self._getMode()
#         if cur_mode != PlaneMovementMode.POSITION:
#             self._plane_rotation_mode_graphic = self.getNearestGraphicsPoint(mouseevent.x(), mouseevent.y())
#             if self._plane_rotation_mode_graphic:
#                 self._active_mode.setActive()
#
#             self._previous_mouse_position = [mouseevent.x(), mouseevent.y()]
#
#             if not self._active_mode.isActive() and cur_mode == PlaneMovementMode.NORMAL:
#                 self.processZincMousePressEvent(mouseevent)
#             else:
#                 self._start_plane = PlaneDescription(self._getPointOnPlane(), self._getPlaneNormal(), self._getPlaneNormalGlyphPosition())
#
#         elif mouseevent.modifiers() & QtCore.Qt.CTRL and mouseevent.button() == QtCore.Qt.LeftButton:
#             # If node already at this location then select it and get ready to move it.
#             # otherwise add it and set streaming create mode if appropriate.
#             self._addNode(mouseevent)
#             if self._streaming_create:
#                 self._streaming_create_active = True

    def mouseMoveEvent(self, mouseevent):
        self._active_mode.mouseMoveEvent(mouseevent)
        if not mouseevent.isAccepted():
            super(SceneviewerWidget3D, self).mouseMoveEvent(mouseevent)
#         cur_mode = self._getMode()
#         is_active = self._active_mode.isActive()
#         if is_active and cur_mode == PlaneMovementMode.ROTATION:
#             new_plane_centre = self._calcluatePlaneIntersection(mouseevent.x(), mouseevent.y())
#             if not new_plane_centre is None:
#                 new_plane_centre = self._boundCoordinatesToElement(new_plane_centre)
#                 self._setPointOnPlane(new_plane_centre)
#
#         elif not is_active and cur_mode == PlaneMovementMode.ROTATION:
#             width = self.width()
#             height = self.height()
#             radius = min([width, height]) / 2.0
#             delta_x = float(mouseevent.x() - self._previous_mouse_position[0])
#             delta_y = float(mouseevent.y() - self._previous_mouse_position[1])
#             tangent_dist = sqrt((delta_x * delta_x + delta_y * delta_y))
#             if tangent_dist > 0.0:
#                 dx = -delta_y / tangent_dist;
#                 dy = delta_x / tangent_dist;
#
#                 d = dx * (mouseevent.x() - 0.5 * (width - 1)) + dy * ((mouseevent.y() - 0.5 * (height - 1)))
#                 if d > radius: d = radius
#                 if d < -radius: d = -radius
#
#                 phi = acos(d / radius) - 0.5 * pi
#                 angle = 1.0 * tangent_dist / radius
#
#                 eye, lookat, up = self.getViewParameters()
#
#                 b = up[:]
#                 b = normalize(b)
#                 a = sub(lookat, eye)
#                 a = normalize(a)
#                 c = cross(b, a)
#                 c = normalize(c)
#                 e = [None, None, None]
#                 e[0] = dx * c[0] + dy * b[0]
#                 e[1] = dx * c[1] + dy * b[1]
#                 e[2] = dx * c[2] + dy * b[2]
#                 axis = [None, None, None]
#                 axis[0] = sin(phi) * a[0] + cos(phi) * e[0]
#                 axis[1] = sin(phi) * a[1] + cos(phi) * e[1]
#                 axis[2] = sin(phi) * a[2] + cos(phi) * e[2]
#
#                 plane_normal = self._getPlaneNormal()
#                 point_on_plane = self._getPlaneRotationCentreGlyphPosition()
#
#                 plane_normal_prime_1 = mult(plane_normal, cos(angle))
#                 plane_normal_prime_2 = mult(plane_normal, dot(plane_normal, axis) * (1 - cos(angle)))
#                 plane_normal_prime_3 = mult(cross(axis, plane_normal), sin(angle))
#                 plane_normal_prime = add(add(plane_normal_prime_1, plane_normal_prime_2), plane_normal_prime_3)
#
#                 self._setPlaneEquation(plane_normal_prime, point_on_plane)
#
#                 self._previous_mouse_position = [mouseevent.x(), mouseevent.y()]
#         elif is_active and cur_mode == PlaneMovementMode.NORMAL:
#             pos = self._getPlaneNormalGlyphPosition()  # self._plane_centre_position  # self._getPointOnPlane()
#             screen_pos = self.project(pos[0], pos[1], pos[2])
#             global_cur_pos = self.unproject(mouseevent.x(), -mouseevent.y(), screen_pos[2])
#             global_old_pos = self.unproject(self._previous_mouse_position[0], -self._previous_mouse_position[1], screen_pos[2])
#             global_pos_diff = sub(global_cur_pos, global_old_pos)
#
#             n = self._getPlaneNormal()
#             proj_n = mult(n, dot(global_pos_diff, n))
#             new_pos = add(pos, proj_n)
#             scene = self._iso_graphic.getScene()
#             scene.beginChange()
#             self._setPointOnPlane(new_pos)
#             plane_centre = self._calculatePlaneCentre()
#             if plane_centre is None:
#                 self._setPointOnPlane(pos)
#             else:
#                 self._setPlaneNormalGlyphPosition(plane_centre)
#                 self._setPointOnPlane(plane_centre)
#
#             scene.endChange()
#             self._previous_mouse_position = [mouseevent.x(), mouseevent.y()]
#         elif not is_active and cur_mode == PlaneMovementMode.NORMAL:
#             self.processZincMouseMoveEvent(mouseevent)
#         elif self._streaming_create_active:
#             self._addNode(mouseevent)

    def mouseReleaseEvent(self, mouseevent):
        self._active_mode.mouseReleaseEvent(mouseevent)
        if not mouseevent.isAccepted():
            super(SceneviewerWidget3D, self).mouseReleaseEvent(mouseevent)
#         c = None
#         cur_mode = self._getMode()
#         is_active = self._active_mode.isActive()
#         if not is_active and cur_mode == PlaneMovementMode.ROTATION:
#             plane_centre = self._calculatePlaneCentre()
#             if not plane_centre is None:
#                 self._setPlaneNormalGlyphPosition(plane_centre)
#
#         end_plane = PlaneDescription(self._getPointOnPlane(), self._getPlaneNormal(), self._getPlaneNormalGlyphPosition())
#         if is_active:
#             self._active_mode.setActive(False)
#             c = CommandMovePlane(self._start_plane, end_plane)
#         elif cur_mode == PlaneMovementMode.NORMAL:
#             self.processZincMouseReleaseEvent(mouseevent)
#         elif not self._start_plane is None:
#             c = CommandMovePlane(self._start_plane, end_plane)
#
#         if self._streaming_create:
#             self._streaming_create_active = False
#
#         if not c is None:
#             c.setMethodCallbacks(self._setPlaneNormalGlyphPosition, self._setPlaneEquation)
#             self._undoStack.push(c)


