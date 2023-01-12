"""

"""
from PySide6 import QtGui
from mapclientplugins.segmentationstep.tools.segmentation import SegmentationTool
from mapclientplugins.segmentationstep.undoredo import CommandMovePlane
from mapclientplugins.segmentationstep.plane import PlaneAttitude


class AbstractResetOrientationTool(SegmentationTool):

    def __init__(self, axes, plane, undo_redo_stack):
        super().__init__(f'Reset Orientation {axes}', undo_redo_stack)
        self._icon = QtGui.QIcon(':toolbar_icons/orientation.png')
        # self._icon = QtGui.QIcon(f':toolbar_icons/{axes}.png')
        self._plane = plane
        self._plane_normal = None

    def action(self):
        plane_start = PlaneAttitude(self._plane.getRotationPoint(), self._plane.getNormal())

        point_on_plane = self._plane.getRotationPoint()
        self._plane.setPlaneEquation(self._plane_normal, point_on_plane)

        plane_end = PlaneAttitude(self._plane.getRotationPoint(), self._plane.getNormal())

        c = CommandMovePlane(self._plane, plane_start, plane_end)
        self._undo_redo_stack.push(c)


class ResetOrientationXYTool(AbstractResetOrientationTool):
    def __init__(self, plane, undo_redo_stack):
        super().__init__('XY', plane, undo_redo_stack)
        self._plane_normal = [0.0, 0.0, 1.0]


class ResetOrientationXZTool(AbstractResetOrientationTool):
    def __init__(self, plane, undo_redo_stack):
        super().__init__('XZ', plane, undo_redo_stack)
        self._plane_normal = [0.0, 1.0, 0.0]


class ResetOrientationYZTool(AbstractResetOrientationTool):
    def __init__(self, plane, undo_redo_stack):
        super().__init__('YZ', plane, undo_redo_stack)
        self._plane_normal = [1.0, 0.0, 0.0]
