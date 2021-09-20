"""

"""

from PySide2 import QtGui
from mapclientplugins.segmentationstep.plane import PlaneAttitude
from mapclientplugins.segmentationstep.definitions import ViewMode
from mapclientplugins.segmentationstep.undoredo import CommandMovePlane
from mapclientplugins.segmentationstep.zincutils import setGlyphPosition
from mapclientplugins.segmentationstep.commands.abstractcommand import AbstractCommand


class AbstractResetOrientationCommand(AbstractCommand):

    def __init__(self, axes, plane, undo_redo_stack, cuboid_dimensions, active_handler):
        super().__init__(f'Reset Orientation {axes}')
        self._icon = QtGui.QIcon(':toolbar_icons/orientation.png')
        # self._icon = QtGui.QIcon(f':toolbar_icons/{axes}.png')
        self._plane = plane
        self._plane_normal = None
        self._undo_redo_stack = undo_redo_stack

        self._cuboid_dimensions = cuboid_dimensions
        self._current_handler = active_handler

        if axes == "XY":
            self._normal_axis = 2
        elif axes == "XZ":
            self._normal_axis = 1
        else:
            self._normal_axis = 0

    def get_function(self):
        return self.execute

    def execute(self):
        plane_start = PlaneAttitude(self._plane.getRotationPoint(), self._plane.getNormal())

        point_on_plane = self._plane.getRotationPoint()
        new_point_on_plane = [0, 0, 0]

        for i in range(3):
            if i == self._normal_axis:
                new_point_on_plane[i] = point_on_plane[i]
            else:
                new_point_on_plane[i] = self._cuboid_dimensions[i] / 2

        self._plane.setPlaneEquation(self._plane_normal, new_point_on_plane)

        current_handler = self._current_handler()
        if current_handler.getModeType() == ViewMode.PLANE_NORMAL or current_handler.getModeType() == ViewMode.PLANE_ROTATION:
            setGlyphPosition(current_handler.getGlyph(), new_point_on_plane)

        plane_end = PlaneAttitude(self._plane.getRotationPoint(), self._plane.getNormal())

        c = CommandMovePlane(self._plane, plane_start, plane_end)
        self._undo_redo_stack.push(c)


class ResetOrientationXYCommand(AbstractResetOrientationCommand):
    def __init__(self, plane, undo_redo_stack, cuboid_dimensions, active_handler):
        super().__init__('XY', plane, undo_redo_stack, cuboid_dimensions, active_handler)
        self._plane_normal = [0.0, 0.0, 1.0]


class ResetOrientationXZCommand(AbstractResetOrientationCommand):
    def __init__(self, plane, undo_redo_stack, cuboid_dimensions, active_handler):
        super().__init__('XZ', plane, undo_redo_stack, cuboid_dimensions, active_handler)
        self._plane_normal = [0.0, 1.0, 0.0]


class ResetOrientationYZCommand(AbstractResetOrientationCommand):
    def __init__(self, plane, undo_redo_stack, cuboid_dimensions, active_handler):
        super().__init__('YZ', plane, undo_redo_stack, cuboid_dimensions, active_handler)
        self._plane_normal = [1.0, 0.0, 0.0]
