"""

"""
from PySide2 import QtGui
from mapclientplugins.segmentationstep.tools.segmentation import SegmentationTool
from mapclientplugins.segmentationstep.zincutils import createPlaneManipulationSphere


class AbstractResetOrientationTool(SegmentationTool):

    def __init__(self, axes, plane, undo_redo_stack):
        super().__init__(f'Reset Orientation {axes}', undo_redo_stack)
        self._icon = QtGui.QIcon(':toolbar_icons/orientation.png')
        # self._icon = QtGui.QIcon(f':toolbar_icons/{axes}.png')
        self._plane = plane
        self._plane_normal = None

    def action(self):
        # The undo and redo actions for this method don't always work correctly.

        glyph = createPlaneManipulationSphere(self._plane.getRegion())
        scene = glyph.getScene()
        scene.beginChange()

        point_on_plane = self._plane.getRotationPoint()
        self._plane.setPlaneEquation(self._plane_normal, point_on_plane)

        scene.endChange()


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
