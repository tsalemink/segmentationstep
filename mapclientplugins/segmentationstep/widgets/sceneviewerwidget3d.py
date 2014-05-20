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

from mapclientplugins.segmentationstep.widgets.sceneviewerwidget import SceneviewerWidget
from mapclientplugins.segmentationstep.widgets.definitions import PlaneMovementMode
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

        position_mode = PositionMode(plane, self._undoStack)

        normal_mode = NormalMode(plane, self._undoStack)
        normal_mode.setGlyphPickerMethod(self.getNearestGraphicsPoint)
        normal_mode.setGetDimensionsMethod(model.getDimensions)
        normal_mode.setProjectUnProjectMethods(self.project, self.unproject)
        normal_mode.setDefaultMaterial(yellow_material)
        normal_mode.setSelectedMaterial(orange_material)

        rotation_mode = RotationMode(plane, self._undoStack)
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
        self.setUndoStack(model.getUndoRedoStack())
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

    def mouseMoveEvent(self, mouseevent):
        self._active_mode.mouseMoveEvent(mouseevent)
        if not mouseevent.isAccepted():
            super(SceneviewerWidget3D, self).mouseMoveEvent(mouseevent)

    def mouseReleaseEvent(self, mouseevent):
        self._active_mode.mouseReleaseEvent(mouseevent)
        if not mouseevent.isAccepted():
            super(SceneviewerWidget3D, self).mouseReleaseEvent(mouseevent)


