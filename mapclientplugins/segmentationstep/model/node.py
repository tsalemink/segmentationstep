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
import json

from opencmiss.zinc.status import OK

from mapclientplugins.segmentationstep.model.abstractmodel import AbstractModel
from mapclientplugins.segmentationstep.zincutils import createFiniteElementField
from mapclientplugins.segmentationstep.segmentpoint import SegmentPointStatus
from mapclientplugins.segmentationstep.model.curve import CurveModel
from mapclientplugins.segmentationstep.plane import PlaneAttitude

class NodeModel(AbstractModel):

    def __init__(self, context, plane):
        super(NodeModel, self).__init__(context)
        self._attributes_that_auto_serialize = [ "_nodes", "_plane_attitudes"]
        self._plane = plane
        self._plane_attitude_store = []
        self._plane_attitudes = {}
        self._nodes = {}
        self._curves = {}
        self._setupNodeRegion()
        self._on_plane_conditional_field = self._createOnPlaneConditionalField()
        self._on_plane_point_cloud_field = self._createOnPlanePointCloudField()
        self._on_plane_curve_field = self._createOnPlaneCurveField()
        self._on_plane_interpolation_point_field = self._createOnPlaneInterpolation()

    def getPointCloud(self):
        cloud = []
        node_nodeset = self._point_cloud_group.getMasterNodeset()
        datapoint_nodeset = self._interpolation_point_group.getMasterNodeset()
        def _getLocations(nodeset):
            locations = []
            ni = nodeset.createNodeiterator()
            node = ni.next()
            while node.isValid():
                locations.append(self.getNodeLocation(node))
                node = ni.next()

            return locations

        cloud += _getLocations(node_nodeset)
        cloud += _getLocations(datapoint_nodeset)
        return cloud

    def _serializeNodeset(self, group):
        str_rep = ''
        ni = group.createNodeiterator()
        node = ni.next()
        while node.isValid():
            str_rep += '"' + str(node.getIdentifier()) + '":' + json.dumps(self.getNodeLocation(node))
            node = ni.next()
            if node.isValid():
                str_rep += ','

        return str_rep

    def _serializeSelection(self):
        node_ids = []
        ni = self._group.createNodeiterator()
        node = ni.next()
        while node.isValid():
            node_ids.append(node.getIdentifier())
            node = ni.next()

        return json.dumps(node_ids)

    def serialize(self):
        str_rep = '{'
        str_rep += '"_basic_points":{' + self._serializeNodeset(self._point_cloud_group)
        str_rep += '},'
        str_rep += '"_curve_points":{' + self._serializeNodeset(self._curve_group)
        str_rep += '},'
        str_rep += '"_interpolation_points":{' + self._serializeNodeset(self._interpolation_point_group)
        str_rep += '},'
        str_rep += '"_selection":' + self._serializeSelection()
        str_rep += ','
        str_rep += '"_plane":' + self._plane.serialize() + ','
        str_rep += '"_curves":{ '  # this space after the curly bracket is very important do not remove it.
        for curve_index in self._curves:
            str_rep += '"' + str(curve_index) + '":' + self._curves[curve_index].serialize() + ','
        str_rep = str_rep[:-1] + '},'
        str_rep += '"_plane_attitude_store":['
        for plane_attitude in self._plane_attitude_store:
            str_rep += plane_attitude.serialize()
            if plane_attitude != self._plane_attitude_store[-1]:
                str_rep += ', '
        str_rep += '],'

        for attr in self._attributes_that_auto_serialize:
            str_rep += '"' + attr + '":' + json.dumps(getattr(self, attr))
            if attr != self._attributes_that_auto_serialize[-1]:
                str_rep += ','

        str_rep += '}'
        return str_rep

    def _deserializeNodeset(self, group, data):
        for node_id in data:
            node = self._createNodeAtLocation(data[node_id], group.getName(), int(node_id))
            group.addNode(node)

    def _deserializeSelection(self, data):
        for node_id in data:
            node = self.getNodeByIdentifier(node_id)
            self._group.addNode(node)

    def deserialize(self, str_rep):
        scene = self._region.getScene()
        scene.beginChange()
        master_nodeset = self._point_cloud_group.getMasterNodeset()  # removeAllNodes()
        master_nodeset.destroyAllNodes()
        master_nodeset = self._interpolation_point_group.getMasterNodeset()
        master_nodeset.destroyAllNodes()
        self.setSelection([])

        d = json.loads(str_rep)

        self._deserializeNodeset(self._point_cloud_group, d['_basic_points'])
        del d['_basic_points']
        self._deserializeNodeset(self._curve_group, d['_curve_points'])
        del d['_curve_points']
        self._deserializeNodeset(self._interpolation_point_group, d['_interpolation_points'])
        del d['_interpolation_points']
        self._plane.deserialize(json.dumps(d['_plane']))
        del d['_plane']
        self._curves = {}
        curves = d['_curves']
        for curve_index in curves:
            c = CurveModel(self)
            c.deserialize(json.dumps(curves[curve_index]))
            self._curves[int(curve_index)] = c
        del d['_curves']
        self._plane_attitude_store = []
        plane_attitude_store = d['_plane_attitude_store']
        for plane_attitude in plane_attitude_store:
            p = PlaneAttitude(None, None)
            p.deserialize(json.dumps(plane_attitude))
            self._plane_attitude_store.append(p)
        del d['_plane_attitude_store']
        selection = d['_selection']
        selection_field = scene.getSelectionField()
        if not selection_field.isValid():
            scene.setSelectionField(self._selection_group_field)
        del d['_selection']

        self.__dict__.update(d)
        self.setSelection(selection)
        scene.endChange()

    def _setupNodeRegion(self):
        self._region = self._context.getDefaultRegion().createChild('point_cloud')
#         scene = self._region.getScene()
        self._coordinate_field = createFiniteElementField(self._region)
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()
        nodeset = fieldmodule.findNodesetByName('nodes')

        self._scale_field = fieldmodule.createFieldConstant([1.0, 1.0, 1.0])
        self._scaled_coordinate_field = self._coordinate_field * self._scale_field

        # Setup the selection fields
        self._selection_group_field = fieldmodule.createFieldGroup()
        selectiongroup = self._selection_group_field.createFieldNodeGroup(nodeset)
        self._group = selectiongroup.getNodesetGroup()

        # Setup the point cloud fields
        self._point_cloud_group_field = fieldmodule.createFieldGroup()
        pointcloudgroup = self._point_cloud_group_field.createFieldNodeGroup(nodeset)
        self._point_cloud_group = pointcloudgroup.getNodesetGroup()

        # Setup the curve fields
        self._curve_group_field = fieldmodule.createFieldGroup()
        curvegroup = self._curve_group_field.createFieldNodeGroup(nodeset)
        self._curve_group = curvegroup.getNodesetGroup()

        datapointset = fieldmodule.findNodesetByName('datapoints')
        self._interpolation_point_group_field = fieldmodule.createFieldGroup()
        segmentationpointgroup = self._curve_group_field.createFieldNodeGroup(datapointset)
        self._interpolation_point_group = segmentationpointgroup.getNodesetGroup()

        fieldmodule.endChange()

    def _createOnPlaneConditionalField(self):
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()

        alias_normal_field = fieldmodule.createFieldAlias(self._plane.getNormalField())
        alias_point_field = fieldmodule.createFieldAlias(self._plane.getRotationPointField())

        plane_equation_field = self._createPlaneEquationField(fieldmodule, self._scaled_coordinate_field, alias_normal_field, alias_point_field)
        tolerance_field = fieldmodule.createFieldConstant(0.5)
        abs_field = fieldmodule.createFieldAbs(plane_equation_field)
        on_plane_field = fieldmodule.createFieldLessThan(abs_field, tolerance_field)

        fieldmodule.endChange()
        return on_plane_field

    def _createOnPlanePointCloudField(self):
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()
        and_field = fieldmodule.createFieldAnd(self._on_plane_conditional_field, self._point_cloud_group_field)
        fieldmodule.endChange()

        return and_field

    def _createOnPlaneCurveField(self):
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()
        and_field = fieldmodule.createFieldAnd(self._on_plane_conditional_field, self._curve_group_field)
        fieldmodule.endChange()

        return and_field

    def _createOnPlaneInterpolation(self):
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()
        and_field = fieldmodule.createFieldAnd(self._on_plane_conditional_field, self._interpolation_point_group_field)
        fieldmodule.endChange()

        return and_field

    def _createPlaneEquationField(self, fieldmodule, coordinate_field, plane_normal_field, point_on_plane_field):
        d = fieldmodule.createFieldDotProduct(plane_normal_field, point_on_plane_field)
        plane_equation_field = fieldmodule.createFieldDotProduct(coordinate_field, plane_normal_field) - d

        return plane_equation_field

    def setScale(self, scale):
        '''
        Don't call this 'setScale' method directly let the main model do that
        this way we can ensure that the two scale fields have the same
        values.
        '''
        fieldmodule = self._region.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        self._scale_field.assignReal(fieldcache, scale)

    def getPointCloudGroupField(self):
        return self._point_cloud_group_field

    def getPointCloudGroup(self):
        return self._point_cloud_group

    def getCurveGroupField(self):
        return self._curve_group_field

    def getCurveGroup(self):
        return self._curve_group

    def getInterpolationPointGroup(self):
        return self._interpolation_point_group

    def getOnPlanePointCloudField(self):
        return self._on_plane_point_cloud_field

    def getOnPlaneInterpolationField(self):
        return self._on_plane_conditional_field

    def getOnPlaneCurveField(self):
        return self._on_plane_curve_field

    def getOnPlaneSegmentationPointField(self):
        return self._on_plane_conditional_field

    def getSelectionGroupField(self):
        return self._selection_group_field

    def getSelectionGroup(self):
        return self._group

    def isSelected(self, node):
        return self._group.containsNode(node)

    def getCurrentSelection(self):
        selection = []
        ni = self._group.createNodeiterator()
        node = ni.next()
        while node.isValid():
            selection.append(node.getIdentifier())
            node = ni.next()

        return selection

    def setSelection(self, selection):
        fieldmodule = self._region.getFieldmodule()
        nodeset = self._group.getMasterNodeset()  # fieldmodule.findNodesetByName('nodes')
        fieldmodule.beginChange()
        self._selection_group_field.clear()
        for node_id in selection:
            node = nodeset.findNodeByIdentifier(node_id)
            self._group.addNode(node)
            if node_id == selection[0]:
                plane_attitude = self.getNodePlaneAttitude(node_id)
                self._plane.setPlaneEquation(plane_attitude.getNormal(), plane_attitude.getPoint())

        fieldmodule.endChange()

    def getNodeByIdentifier(self, node_id):
        fieldmodule = self._region.getFieldmodule()
        nodeset = fieldmodule.findNodesetByName('nodes')
        node = nodeset.findNodeByIdentifier(node_id)
        return node

    def getNodePlaneAttitude(self, node_id):
        return self._plane_attitude_store[self._nodes[str(node_id)]]

    def getNodeStatus(self, node_id):
        node = self.getNodeByIdentifier(node_id)
        node_status = SegmentPointStatus(node_id, self.getNodeLocation(node), self.getNodePlaneAttitude(node_id))
        return node_status

    def _addId(self, plane_attitude, node_id):
        if plane_attitude in self._plane_attitude_store:
            index = self._plane_attitude_store.index(plane_attitude)
            self._plane_attitudes[str(index)].append(node_id)
        else:
            if None in self._plane_attitude_store:
                index = self._plane_attitude_store.index(None)
                self._plane_attitude_store[index] = plane_attitude
            else:
                index = len(self._plane_attitude_store)
                self._plane_attitude_store.append(plane_attitude)

            self._plane_attitudes[str(index)] = [node_id]

    def _removeId(self, plane_attitude, node_id):
        plane_attitude_index = self._plane_attitude_store.index(plane_attitude)
        index = self._plane_attitudes[str(plane_attitude_index)].index(node_id)
        del self._plane_attitudes[str(plane_attitude_index)][index]
        if len(self._plane_attitudes[str(plane_attitude_index)]) == 0:
            del self._plane_attitudes[str(plane_attitude_index)]
            self._plane_attitude_store[plane_attitude_index] = None

    def getElementByIdentifier(self, element_id):
        fieldmodule = self._region.getFieldmodule()
        mesh = fieldmodule.findMeshByDimension(1)
        if element_id is None:
            element_id = -1
        return mesh.findElementByIdentifier(element_id)

    def getCurveCount(self):
        return len(self._curves)

    def insertCurve(self, curve_identifier, curve):
        self._curves[curve_identifier] = curve

    def popCurve(self, curve_identifier):
        if curve_identifier in self._curves:
            curve = self._curves[curve_identifier]
            del self._curves[curve_identifier]
            node_ids = curve.getNodes()
            for node_id in node_ids:
                self.removeNode(node_id)
            curve.removeAllNodes()

    def getCurveIdentifier(self, curve):
        for curve_identifier in self._curves:
            if curve == self._curves[curve_identifier]:
                return curve_identifier

        return None

    def getCurveWithIdentifier(self, index):
        return self._curves[index]

    def getCurveForNode(self, node_id):
        for curve_identifier in self._curves:
            curve = self._curves[curve_identifier]
            if node_id in curve:
                return curve

        return None

    def addNode(self, node_id, location, plane_attitude):
        if node_id is -1:
            node = self._createNodeAtLocation(location)
            node_id = node.getIdentifier()
        self._addId(plane_attitude, node_id)
        self._nodes[str(node_id)] = self._plane_attitude_store.index(plane_attitude)

        return node_id

    def addNodes(self, node_statuses):
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()

        node_ids = []
        for node_status in node_statuses:
            node_id = self.addNode(node_status.getNodeIdentifier(), node_status.getLocation(), node_status.getPlaneAttitude())
            node_ids.append(node_id)

        fieldmodule.endChange()

    def modifyNode(self, node_id, location, plane_attitude):
        current_plane_attitude = self._plane_attitude_store[self._nodes[str(node_id)]]
        node = self.getNodeByIdentifier(node_id)
        self.setNodeLocation(node, location)
        if current_plane_attitude != plane_attitude:
            self._removeId(current_plane_attitude, node_id)
            self._addId(plane_attitude, node_id)
            self._nodes[str(node_id)] = self._plane_attitude_store.index(plane_attitude)

    def setNodeLocation(self, node, location):
        fieldmodule = self._region.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        fieldcache.setNode(node)
        self._coordinate_field.assignReal(fieldcache, location)
        fieldmodule.endChange()

    def getNodeLocation(self, node):
        fieldmodule = self._region.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        fieldcache.setNode(node)
        result, location = self._coordinate_field.evaluateReal(fieldcache, 3)
        fieldmodule.endChange()

        if result == OK:
            return location

        return None

    def removeElement(self, element_id):
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()
        mesh = fieldmodule.findMeshByDimension(1)
        element = mesh.findElementByIdentifier(element_id)
        mesh.destroyElement(element)
        fieldmodule.endChange()

    def createDatapoint(self, location=None):
        node = self._createNodeAtLocation(location, 'datapoints')
        self._interpolation_point_group.addNode(node)
        return node

    def removeDatapoint(self, datapoint):
        nodeset = datapoint.getNodeset()
        nodeset.destroyNode(datapoint)

    def removeNodes(self, node_statuses):
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()

        for node_status in node_statuses:
            self.removeNode(node_status.getNodeIdentifier())

        fieldmodule.endChange()

    def removeNode(self, node_id):
        if str(node_id) in self._nodes:
            plane_attitude = self._plane_attitude_store[self._nodes[str(node_id)]]
            self._removeId(plane_attitude, node_id)
            del self._nodes[str(node_id)]

        node = self.getNodeByIdentifier(node_id)
        nodeset = node.getNodeset()
        nodeset.destroyNode(node)

    def createNodes(self, node_statuses, group=None):
        node_ids = []
        for node_status in node_statuses:
            node_id = self.addNode(-1, node_status.getLocation(), node_status.getPlaneAttitude())
            if group is not None:
                node = self.getNodeByIdentifier(node_id)
                group.addNode(node)
            node_ids.append(node_id)

        return node_ids

    def createNode(self):
        '''
        Create a node with the models coordinate field.
        '''
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()

        nodeset = fieldmodule.findNodesetByName('nodes')
        template = nodeset.createNodetemplate()
        template.defineField(self._coordinate_field)

        scene = self._region.getScene()
        selection_field = scene.getSelectionField()
        if not selection_field.isValid():
            scene.setSelectionField(self._selection_group_field)

        self._selection_group_field.clear()

        node = nodeset.createNode(-1, template)
        self._group.addNode(node)

        fieldmodule.endChange()

        return node

    def _createNodeAtLocation(self, location, dataset='nodes', node_id=-1):
        '''
        Creates a node at the given location without
        adding it to the current selection.
        '''
        fieldmodule = self._region.getFieldmodule()
        fieldmodule.beginChange()

        nodeset = fieldmodule.findNodesetByName(dataset)
        template = nodeset.createNodetemplate()
        template.defineField(self._coordinate_field)
        node = nodeset.createNode(node_id, template)
        self.setNodeLocation(node, location)
        fieldmodule.endChange()

        return node
