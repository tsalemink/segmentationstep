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
from PySide import QtCore

from mapclientplugins.segmentationstep.viewmodes.abstractviewmode import AbstractViewMode
from mapclientplugins.segmentationstep.widgets.definitions import ViewMode

class SelectionMode(object):

    NONE = -1
    EXCULSIVE = 0
    ADDITIVE = 1

class SegmentMode(AbstractViewMode):

    def __init__(self, sceneviewer, plane, undo_redo_stack):
        super(SegmentMode, self).__init__(sceneviewer, plane, undo_redo_stack)
        self._mode_type = ViewMode.SEGMENT
        self._model = None

#     def _setSceneviewerFilters(self):
#         filtermodule = self._context.getScenefiltermodule()
# #         node_filter = filtermodule.createScenefilterFieldDomainType(Field.DOMAIN_TYPE_NODES)
#         visibility_filter = filtermodule.createScenefilterVisibilityFlags()
#         label_filter1 = filtermodule.createScenefilterGraphicsName(IMAGE_PLANE_GRAPHIC_NAME)
#         label_filter2 = filtermodule.createScenefilterGraphicsName(POINT_CLOUD_GRAPHIC_NAME)
# #         label_filter1.setInverse(True)
#
#         label_filter = filtermodule.createScenefilterOperatorOr()
#         label_filter.appendOperand(label_filter1)
#         label_filter.appendOperand(label_filter2)
#
#         master_filter = filtermodule.createScenefilterOperatorAnd()
# #         master_filter.appendOperand(node_filter)
#         master_filter.appendOperand(visibility_filter)
#         master_filter.appendOperand(label_filter)
#
#         self._sceneviewer.setScenefilter(master_filter)
    def setModel(self, model):
        self._model = model

    def mousePressEvent(self, event):
        super(SegmentMode, self).mousePressEvent(event)
        self._selectionMode = SelectionMode.NONE
        if event.modifiers() & QtCore.Qt.SHIFT and event.button() == QtCore.Qt.LeftButton:
            self._selectionPositionStart = [event.x(), event.y()]
            self._selectionMode = SelectionMode.EXCULSIVE
            if event.modifiers() & QtCore.Qt.ALT:
                self._selectionMode = SelectionMode.ADDITIVE

    def mouseMoveEvent(self, event):
        super(SegmentMode, self).mouseMoveEvent(event)
        if self._selectionMode != SelectionMode.NONE:
            x = event.x()
            y = event.y()
            xdiff = float(x - self._selectionPositionStart[0])
            ydiff = float(y - self._selectionPositionStart[1])
            if abs(xdiff) < 0.0001:
                xdiff = 1
            if abs(ydiff) < 0.0001:
                ydiff = 1
            xoff = float(self._selectionPositionStart[0]) / xdiff + 0.5
            yoff = float(self._selectionPositionStart[1]) / ydiff + 0.5
            scene = self._selection_box.getScene()
            scene.beginChange()
            self._selectionBox_setBaseSize([xdiff, ydiff, 0.999])
            self._selectionBox_setGlyphOffset([xoff, -yoff, 0])
            self._selection_box.setVisibilityFlag(True)
            scene.endChange()

    def mouseReleaseEvent(self, event):
        super(SegmentMode, self).mouseReleaseEvent(event)
        if self._selectionMode != SelectionMode.NONE:
            x = event.x()
            y = event.y()
            # Construct a small frustrum to look for nodes in.
            root_region = self._view._context.getDefaultRegion()
            root_region.beginHierarchicalChange()
            self._selection_box.setVisibilityFlag(False)

            if (x != self._selectionPositionStart[0] and y != self._selectionPositionStart[1]):
                left = min(x, self._selectionPositionStart[0])
                right = max(x, self._selectionPositionStart[0])
                bottom = min(y, self._selectionPositionStart[1])
                top = max(y, self._selectionPositionStart[1])
                self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, left, bottom, right, top);
                if self._selectionMode == SelectionMode.EXCULSIVE:
                    self._selectionGroup.clear()
                if self._nodeSelectMode:
                    self._scenepicker.addPickedNodesToFieldGroup(self._selectionGroup)
                if self._elemSelectMode:
                    self._scenepicker.addPickedElementsToFieldGroup(self._selectionGroup)
            else:

                self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, x - 0.5, y - 0.5, x + 0.5, y + 0.5)
                if self._nodeSelectMode and self._elemSelectMode and self._selectionMode == SelectionMode.EXCULSIVE and not self._scenepicker.getNearestGraphics().isValid():
                    self._selectionGroup.clear()

                if self._nodeSelectMode and (self._scenepicker.getNearestGraphics().getFieldDomainType() == Field.DOMAIN_TYPE_NODES):
                    node = self._scenepicker.getNearestNode()
                    nodeset = node.getNodeset()

                    nodegroup = self._selectionGroup.getFieldNodeGroup(nodeset)
                    if not nodegroup.isValid():
                        nodegroup = self._selectionGroup.createFieldNodeGroup(nodeset)

                    group = nodegroup.getNodesetGroup()
                    if self._selectionMode == SelectionMode.EXCULSIVE:
                        remove_current = group.getSize() == 1 and group.containsNode(node)
                        self._selectionGroup.clear()
                        if not remove_current:
                            group.addNode(node)
                    elif self._selectionMode == SelectionMode.ADDITIVE:
                        if group.containsNode(node):
                            group.removeNode(node)
                        else:
                            group.addNode(node)

                if self._elemSelectMode and (self._scenepicker.getNearestGraphics().getFieldDomainType() in [Field.DOMAIN_TYPE_MESH1D, Field.DOMAIN_TYPE_MESH2D, Field.DOMAIN_TYPE_MESH3D, Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION]):
                    elem = self._scenepicker.getNearestElement()
                    mesh = elem.getMesh()

                    elementgroup = self._selectionGroup.getFieldElementGroup(mesh)
                    if not elementgroup.isValid():
                        elementgroup = self._selectionGroup.createFieldElementGroup(mesh)

                    group = elementgroup.getMeshGroup()
                    if self._selectionMode == SelectionMode.EXCULSIVE:
                        remove_current = group.getSize() == 1 and group.containsElement(elem)
                        self._selectionGroup.clear()
                        if not remove_current:
                            group.addElement(elem)
                    elif self._selectionMode == SelectionMode.ADDITIVE:
                        if group.containsElement(elem):
                            group.removeElement(elem)
                        else:
                            group.addElement(elem)


            root_region.endHierarchicalChange()
            self._selectionMode = SelectionMode.NONE


