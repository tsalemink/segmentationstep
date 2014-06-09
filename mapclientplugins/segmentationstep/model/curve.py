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
# from mapclientplugins.segmentationstep.zincutils import create1DFiniteElement
from mapclientplugins.segmentationstep.maths.algorithms import paramerterizedSplines, \
    evaluatePolynomial
from mapclientplugins.segmentationstep.definitions import DEFAULT_INTERPOLATION_COUNT

class CurveModel(object):

    def __init__(self, node_model):
        self._node_model = node_model
        self._nodes = []
#         self._elements = []
        self._closed = False
        self._interpolation_count = DEFAULT_INTERPOLATION_COUNT

    def getNodes(self):
        return self._nodes

    def setNodes(self, node_ids):
        self._nodes = node_ids

    def getInterpolationCount(self):
        return self._interpolation_count

    def setInterpolationCount(self, count):
        self._interpolation_count = count

    def calculate(self):
        data = [self._node_model.getNodeLocation(self._node_model.getNodeByIdentifier(node_id)) for node_id in self._nodes]
        if self.isClosed():
            data += [self._node_model.getNodeLocation(self._node_model.getNodeByIdentifier(self._nodes[0]))]
        splines = paramerterizedSplines(data)
        t = [float(i) / (self._interpolation_count + 1) for i in xrange(1, self._interpolation_count + 1)]  # range(interpolation_point_count)
        locations = []
        for pair in splines:
            xt = pair[0][:]
            yt = pair[1][:]
            zt = pair[2][:]
            for t_i in t:
                x = evaluatePolynomial(t_i, xt)
                y = evaluatePolynomial(t_i, yt)
                z = evaluatePolynomial(t_i, zt)
                locations.append([x, y, z])

        return locations

    def addNode(self, node_id):
        if node_id not in self._nodes:
#             if self._nodes:
#                 first_node_id = self._nodes[-1]
#                 self._elements.append(self._createElement(first_node_id, node_id))
            self._nodes.append(node_id)
        elif self.closes(node_id):
#             first_node_id = self._nodes[-1]
#             self._elements.append(self._createElement(first_node_id, node_id))
            self._closed = True

    def removeNode(self, node_id):
        if node_id in self._nodes:
#             if self.isClosed() and node_id == self._nodes[0]:
#                 self._removeElement(self._elements[-1])
#                 del self._elements[-1]
#             else:
                index = self._nodes.index(node_id)
#                 [self._removeElement(element_id) for element_id in self._elements[(index - 1):]]
#                 del self._elements[(index - 1):]
                del self._nodes[index:]
                self._closed = False

    def removeAllNodes(self):
        self._nodes = []
        self._closed = False

    def closes(self, node_id):
        cl = False
        if len(self._nodes) > 2 and node_id == self._nodes[0]:
            cl = True

        return cl

    def isClosed(self):
        return self._closed

#     def _removeElement(self, element_id):
#         region = self._node_model.getRegion()
#         fieldmodule = region.getFieldmodule()
#         mesh = fieldmodule.findMeshByDimension(1)
#         element = mesh.findElementByIdentifier(element_id)
#         mesh.destroyElement(element)
#
#     def _createElement(self, node_id1, node_id2):
#         node1 = self._node_model.getNodeByIdentifier(node_id1)
#         node2 = self._node_model.getNodeByIdentifier(node_id2)
#         element = create1DFiniteElement(self._node_model.getCoordinateField(), node1, node2)
#
#         return element.getIdentifier()

    def __len__(self):
        return len(self._nodes)

    def __contains__(self, key):
        return key in self._nodes


