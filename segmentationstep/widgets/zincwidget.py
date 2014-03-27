# This python module is intended to facilitate users creating their own applications that use OpenCMISS-Zinc
# See the examples at https://svn.physiomeproject.org/svn/cmiss/zinc/bindings/trunk/python/ for further
# information.

try:
    from PySide import QtCore, QtOpenGL
except ImportError:
    from PyQt4 import QtCore, QtOpenGL

# from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.sceneviewer import Sceneviewer, Sceneviewerevent
from opencmiss.zinc.sceneviewerinput import Sceneviewerinput
from opencmiss.zinc.element import Element, Elementbasis
from opencmiss.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_LOCAL, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, SCENECOORDINATESYSTEM_WORLD
from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.status import OK

from segmentationstep.undoredo import CommandChangeView

# mapping from qt to zinc start
# Create a button map of Qt mouse buttons to Zinc input buttons
button_map = {QtCore.Qt.LeftButton: Sceneviewerinput.BUTTON_TYPE_LEFT, QtCore.Qt.MidButton: Sceneviewerinput.BUTTON_TYPE_MIDDLE, QtCore.Qt.RightButton: Sceneviewerinput.BUTTON_TYPE_RIGHT}
# Create a modifier map of Qt modifier keys to Zinc modifier keys
def modifier_map(qt_modifiers):
    '''
    Return a Zinc SceneViewerInput modifiers object that is created from
    the Qt modifier flags passed in.
    '''
    modifiers = Sceneviewerinput.MODIFIER_FLAG_NONE
    if qt_modifiers & QtCore.Qt.SHIFT:
        modifiers = modifiers | Sceneviewerinput.MODIFIER_FLAG_SHIFT

    return modifiers
# mapping from qt to zinc end

# projectionMode start
class ProjectionMode(object):

    PARALLEL = 0
    PERSPECTIVE = 1
# projectionMode end


# selectionMode start
class SelectionMode(object):

    NONE = -1
    EXCULSIVE = 0
    ADDITIVE = 1
# selectionMode end


class ViewportParameters(object):

    def __init__(self, eye, lookat, up):
        self._eye = eye
        self._lookat = lookat
        self._up = up

    def getEye(self):
        return self._eye

    def getLookat(self):
        return self._lookat

    def getUp(self):
        return self._up


class ZincWidget(QtOpenGL.QGLWidget):

    # Create a signal to notify when the sceneviewer is ready.
    graphicsInitialized = QtCore.Signal()

    # init start
    def __init__(self, parent=None):
        '''
        Call the super class init functions, set the  Zinc context and the scene viewer handle to None.
        Initialise other attributes that deal with selection and the rotation of the plane.
        '''
        QtOpenGL.QGLWidget.__init__(self, parent)
        # Create a Zinc context from which all other objects can be derived either directly or indirectly.
        self._context = None
        self._sceneviewer = None

        # Selection attributes
        self._nodeSelectMode = True
        self._elemSelectMode = True
        self._selectionMode = SelectionMode.NONE
        self._selectionGroup = None
        self._selectionBox = None
        self._ignore_mouse_events = False
        self._undoStack = None
        # init end

    def setContext(self, context):
        '''
        Sets the context for this ZincWidget.  This should be set before the initializeGL()
        method is called otherwise the scene viewer cannot be created.
        '''
        self._context = context

    def setUndoStack(self, stack):
        self._undoStack = stack

    def getSceneviewer(self):
        '''
        Get the scene viewer for this ZincWidget.
        '''
        return self._sceneviewer

    def setSelectModeNode(self):
        self._nodeSelectMode = True
        self._elemSelectMode = False

    def setSelectModeElement(self):
        self._elemSelectMode = True
        self._nodeSelectMode = False

    def setSelectModeAll(self):
        self._nodeSelectMode = True
        self._elemSelectMode = True

    # initializeGL start
    def initializeGL(self):
        '''
        Initialise the Zinc scene for drawing the axis glyph at a point.  
        '''
        # Get the scene viewer module.
        scene_viewer_module = self._context.getSceneviewermodule()

        # From the scene viewer module we can create a scene viewer, we set up the
        # scene viewer to have the same OpenGL properties as the QGLWidget.
        self._sceneviewer = scene_viewer_module.createSceneviewer(Sceneviewer.BUFFERING_MODE_DOUBLE, Sceneviewer.STEREO_MODE_DEFAULT)
        self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)

        # Create a filter for visibility flags which will allow us to see our graphic.
        filter_module = self._context.getScenefiltermodule()
        # By default graphics are created with their visibility flags set to on (or true).
        graphics_filter = filter_module.createScenefilterVisibilityFlags()

        # Set the graphics filter for the scene viewer otherwise nothing will be visible.
        self._sceneviewer.setScenefilter(graphics_filter)
        region = self._context.getDefaultRegion()
        scene = region.getScene()
        fieldmodule = region.getFieldmodule()
        self._selectionGroup = fieldmodule.createFieldGroup()
        scene.setSelectionField(self._selectionGroup)
        self._scene_picker = scene.createScenepicker()
        self._sceneviewer.setScene(scene)
        self._scene_picker.setScenefilter(graphics_filter)

        self.defineStandardGlyphs()
        self._selectionBox = scene.createGraphicsPoints()
        self._selectionBox.setScenecoordinatesystem(SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT)
        attributes = self._selectionBox.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_CUBE_WIREFRAME)
        attributes.setBaseSize([10, 10, 0.9999])
        attributes.setGlyphOffset([1, -1, 0])
        self._selectionBox_setBaseSize = attributes.setBaseSize
        self._selectionBox_setGlyphOffset = attributes.setGlyphOffset

        self._selectionBox.setVisibilityFlag(False)

        # Set up unproject pipeline
        self._window_coords_from = fieldmodule.createFieldConstant([0, 0, 0])
        self._global_coords_from = fieldmodule.createFieldConstant([0, 0, 0])
        unproject = fieldmodule.createFieldSceneviewerProjection(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, SCENECOORDINATESYSTEM_WORLD)
        project = fieldmodule.createFieldSceneviewerProjection(self._sceneviewer, SCENECOORDINATESYSTEM_WORLD, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT)

#         unproject_t = fieldmodule.createFieldTranspose(4, unproject)
        self._global_coords_to = fieldmodule.createFieldProjection(self._window_coords_from, unproject)
        self._window_coords_to = fieldmodule.createFieldProjection(self._global_coords_from, project)


        self._sceneviewer.viewAll()

#  Not really applicable to us yet.
#         self._selection_notifier = scene.createSelectionnotifier()
#         self._selection_notifier.setCallback(self._zincSelectionEvent)

        self._scene_viewer_notifier = self._sceneviewer.createSceneviewernotifier()
        self._scene_viewer_notifier.setCallback(self._zincSceneviewerEvent)

        self.graphicsInitialized.emit()
        # initializeGL end

    def setProjectionMode(self, mode):
        if mode == ProjectionMode.PARALLEL:
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PARALLEL)
        elif mode == ProjectionMode.PERSPECTIVE:
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)

    def getProjectionMode(self):
        if self._sceneviewer.getProjectionMode() == Sceneviewer.PROJECTION_MODE_PARALLEL:
            return ProjectionMode.PARALLEL
        elif self._sceneviewer.getProjectionMode() == Sceneviewer.PROJECTION_MODE_PERSPECTIVE:
            return ProjectionMode.PERSPECTIVE

    def getViewParameters(self):
        result, eye, lookat, up = self._sceneviewer.getLookatParameters()
        if result == OK:
            return (eye, lookat, up)

        return None

    def setViewParameters(self, eye, lookat, up):
        self._sceneviewer.setLookatParametersNonSkew(eye, lookat, up)

    def project(self, x, y, z):
        in_coords = [x, y, z]
        fieldmodule = self._global_coords_from.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        self._global_coords_from.assignReal(fieldcache, in_coords)
        result, out_coords = self._window_coords_to.evaluateReal(fieldcache, 3)
        if result == OK:
            return out_coords  # [out_coords[0] / out_coords[3], out_coords[1] / out_coords[3], out_coords[2] / out_coords[3]]

        return None

    def unproject(self, x, y, z):
        in_coords = [x, y, z]
        fieldmodule = self._window_coords_from.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        self._window_coords_from.assignReal(fieldcache, in_coords)
        result, out_coords = self._global_coords_to.evaluateReal(fieldcache, 3)
        if result == OK:
            return out_coords  # [out_coords[0] / out_coords[3], out_coords[1] / out_coords[3], out_coords[2] / out_coords[3]]

        return None

    def getViewportSize(self):
        result, width, height = self._sceneviewer.getViewportSize()
        if result == OK:
            return (width, height)

        return None

    def defineStandardGlyphs(self):
        '''
        Helper method to define the standard glyphs.
        '''
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()

    def defineStandardMaterials(self):
        '''
        Helper method to define the standard materials.
        '''
        material_module = self._context.getMaterialmodule()
        material_module.defineStandardMaterials()

    def create3DFiniteElement(self, field_module, finite_element_field, node_coordinate_set):
        '''
        Create finite element from a template
        '''
        # Find a special node set named 'cmiss_nodes'
        nodeset = field_module.findNodesetByName('nodes')
        node_template = nodeset.createNodetemplate()

        # Set the finite element coordinate field for the nodes to use
        node_template.defineField(finite_element_field)
        field_cache = field_module.createFieldcache()

        node_identifiers = []
        # Create eight nodes to define a cube finite element
        for node_coordinate in node_coordinate_set:
            node = nodeset.createNode(-1, node_template)
            node_identifiers.append(node.getIdentifier())
            # Set the node coordinates, first set the field cache to use the current node
            field_cache.setNode(node)
            # Pass in floats as an array
            finite_element_field.assignReal(field_cache, node_coordinate)

        # Use a 3D mesh to to create the 3D finite element.
        mesh = field_module.findMeshByDimension(3)
        element_template = mesh.createElementtemplate()
        element_template.setElementShapeType(Element.SHAPE_TYPE_CUBE)
        element_node_count = 8
        element_template.setNumberOfNodes(element_node_count)
        # Specify the dimension and the interpolation function for the element basis function
        linear_basis = field_module.createElementbasis(3, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
        # the indecies of the nodes in the node template we want to use.
        node_indexes = [1, 2, 3, 4, 5, 6, 7, 8]


        # Define a nodally interpolated element field or field component in the
        # element_template
        element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

        for i, node_identifier in enumerate(node_identifiers):
            node = nodeset.findNodeByIdentifier(node_identifier)
            element_template.setNode(i + 1, node)

        mesh.defineElement(-1, element_template)

    def mapToWidget(self, parent_x, parent_y):
        local_pt = self.mapFromParent(QtCore.QPoint(parent_x, parent_y))
        x = local_pt.x()  # - 4
        y = local_pt.y()  # - 4
        return x, y

    def getNearestGraphicsPoint(self, parent_x, parent_y):
        '''
        Assuming given x and y is in the sending widgets coordinates 
        which is a parent of this widget.  For example the values given 
        directly from the mouseevent in the parent widget.
        '''
        x, y = self.mapToWidget(parent_x, parent_y)
        self._scene_picker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, x - 0.5, y - 0.5, x + 0.5, y + 0.5)
        nearest_graphics = self._scene_picker.getNearestGraphics()
        if nearest_graphics.isValid() and nearest_graphics.getFieldDomainType() == Field.DOMAIN_TYPE_POINT:
            return nearest_graphics

        return None

    def setIgnoreMouseEvents(self, value):
        self._ignore_mouse_events = value

    def viewAll(self):
        '''
        Helper method to set the current scene viewer to view everything
        visible in the current scene.
        '''
        self._sceneviewer.viewAll()

    # paintGL start
    def paintGL(self):
        '''
        Render the scene for this scene viewer.  The QGLWidget has already set up the
        correct OpenGL buffer for us so all we need do is render into it.  The scene viewer
        will clear the background so any OpenGL drawing of your own needs to go after this
        API call.
        '''
        self._sceneviewer.renderScene()
        # paintGL end

    def _zincSceneviewerEvent(self, event):
        '''
        Process a scene viewer event.  The updateGL() method is called for a
        repaint required event all other events are ignored.
        '''
        if event.getChangeFlags() & Sceneviewerevent.CHANGE_FLAG_REPAINT_REQUIRED:
            self.updateGL()

#  Not applicable at the current point in time.
#     def _zincSelectionEvent(self, event):
#         print(event.getChangeFlags())
#         print('go the selection change')

    # resizeGL start
    def resizeGL(self, width, height):
        '''
        Respond to widget resize events.
        '''
        self._sceneviewer.setViewportSize(width, height)
        # resizeGL end

    def mousePressEvent(self, mouseevent):
        '''
        Inform the scene viewer of a mouse press event.
        '''
        self._handle_mouse_events = False  # Track when the zinc should be handling mouse events
        if not self._ignore_mouse_events and (mouseevent.modifiers() & QtCore.Qt.CTRL) and (self._nodeSelectMode or self._elemSelectMode) and button_map[mouseevent.button()] == Sceneviewerinput.BUTTON_TYPE_LEFT:
            self._selectionPositionStart = (mouseevent.x(), mouseevent.y())
            self._selectionMode = SelectionMode.EXCULSIVE
            if mouseevent.modifiers() & QtCore.Qt.SHIFT:
                self._selectionMode = SelectionMode.ADDITIVE
        elif not self._ignore_mouse_events and not mouseevent.modifiers() or mouseevent.modifiers() & QtCore.Qt.SHIFT:
            self.processZincMousePressEvent(mouseevent)
            self._handle_mouse_events = True
        else:
            mouseevent.ignore()

    def mouseReleaseEvent(self, mouseevent):
        '''
        Inform the scene viewer of a mouse release event.
        '''
        if not self._ignore_mouse_events and self._selectionMode != SelectionMode.NONE:
            x = mouseevent.x()
            y = mouseevent.y()
            # Construct a small frustrum to look for nodes in.
            root_region = self._context.getDefaultRegion()
            root_region.beginHierarchicalChange()
            self._selectionBox.setVisibilityFlag(False)

            if (x != self._selectionPositionStart[0] and y != self._selectionPositionStart[1]):
                left = min(x, self._selectionPositionStart[0])
                right = max(x, self._selectionPositionStart[0])
                bottom = min(y, self._selectionPositionStart[1])
                top = max(y, self._selectionPositionStart[1])
                self._scene_picker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, left, bottom, right, top);
                if self._selectionMode == SelectionMode.EXCULSIVE:
                    self._selectionGroup.clear()
                if self._nodeSelectMode:
                    self._scene_picker.addPickedNodesToFieldGroup(self._selectionGroup)
                if self._elemSelectMode:
                    self._scene_picker.addPickedElementsToFieldGroup(self._selectionGroup)
            else:

                self._scene_picker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, x - 0.5, y - 0.5, x + 0.5, y + 0.5)
                if self._nodeSelectMode and self._elemSelectMode and self._selectionMode == SelectionMode.EXCULSIVE and not self._scene_picker.getNearestGraphics().isValid():
                    self._selectionGroup.clear()

                if self._nodeSelectMode and (self._scene_picker.getNearestGraphics().getFieldDomainType() == Field.DOMAIN_TYPE_NODES):
                    node = self._scene_picker.getNearestNode()
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

                if self._elemSelectMode and (self._scene_picker.getNearestGraphics().getFieldDomainType() in [Field.DOMAIN_TYPE_MESH1D, Field.DOMAIN_TYPE_MESH2D, Field.DOMAIN_TYPE_MESH3D, Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION]):
                    elem = self._scene_picker.getNearestElement()
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
        elif not self._ignore_mouse_events and self._handle_mouse_events:
            self.processZincMouseReleaseEvent(mouseevent)
        else:
            mouseevent.ignore()

    def mouseMoveEvent(self, mouseevent):
        '''
        Inform the scene viewer of a mouse move event and update the OpenGL scene to reflect this
        change to the viewport.
        '''

        if not self._ignore_mouse_events and self._selectionMode != SelectionMode.NONE:
            x = mouseevent.x()
            y = mouseevent.y()
            xdiff = float(x - self._selectionPositionStart[0])
            ydiff = float(y - self._selectionPositionStart[1])
            if abs(xdiff) < 0.0001:
                xdiff = 1
            if abs(ydiff) < 0.0001:
                ydiff = 1
            xoff = float(self._selectionPositionStart[0]) / xdiff + 0.5
            yoff = float(self._selectionPositionStart[1]) / ydiff + 0.5
            scene = self._selectionBox.getScene()
            scene.beginChange()
            self._selectionBox_setBaseSize([xdiff, ydiff, 0.999])
            self._selectionBox_setGlyphOffset([xoff, -yoff, 0])
            self._selectionBox.setVisibilityFlag(True)
            scene.endChange()
        elif not self._ignore_mouse_events and self._handle_mouse_events:
            self.processZincMouseMoveEvent(mouseevent)
        else:
            mouseevent.ignore()

    def processZincMousePressEvent(self, mouseevent):
        scene_input = self._sceneviewer.createSceneviewerinput()
        scene_input.setPosition(mouseevent.x(), mouseevent.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_PRESS)
        scene_input.setButtonType(button_map[mouseevent.button()])
        scene_input.setModifierFlags(modifier_map(mouseevent.modifiers()))

        self._sceneviewer.processSceneviewerinput(scene_input)
        p = self.getViewParameters()
        self._start_view_parameters = ViewportParameters(p[0], p[1], p[2])


    def processZincMouseMoveEvent(self, mouseevent):
        scene_input = self._sceneviewer.createSceneviewerinput()
        scene_input.setPosition(mouseevent.x(), mouseevent.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_MOTION_NOTIFY)
        if mouseevent.type() == QtCore.QEvent.Leave:
            scene_input.setPosition(-1, -1)

        self._sceneviewer.processSceneviewerinput(scene_input)

    def processZincMouseReleaseEvent(self, mouseevent):
        scene_input = self._sceneviewer.createSceneviewerinput()
        scene_input.setPosition(mouseevent.x(), mouseevent.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
        scene_input.setButtonType(button_map[mouseevent.button()])

        self._sceneviewer.processSceneviewerinput(scene_input)
        p = self.getViewParameters()
        end_view_parameters = ViewportParameters(p[0], p[1], p[2])
        c = CommandChangeView(self._start_view_parameters, end_view_parameters)
        c.setCallbackMethod(self.setViewParameters)
        self._undoStack.push(c)


