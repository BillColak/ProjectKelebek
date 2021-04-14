import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from nodeeditor.node_scene import Scene
from nodeeditor.node_graphics_view import QDMGraphicsView
from nodeeditor.node_graphics_scene import QDMGraphicsScene

from kelebek_factory_node import FactoryNode
from kelebek_texteditor import KelebekSyntaxHighlighter
from kelebek_factory_sockets import FactorySocketHandler
from kelebek_factory_options import FactoryNodeOptions


from kelebek_conf import get_class_from_opcode, dumpException
DEBUG = False
LISTBOX_MIMETYPE = "application/x-item"


class FactoryGraphicsScene(QDMGraphicsScene):
    def __init__(self, scene: 'Scene', parent: QWidget = None):
        super().__init__(scene, parent)

    def initAssets(self):
        self._color_background = QColor("#A0A0A0")
        self._font_state = QFont("Ubuntu", 16)
        self._font_state.setStyleStrategy(QFont.PreferAntialias)

    def setGrScene(self, width: int, height: int):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter: QPainter, rect: QRect):
        QGraphicsScene.drawBackground(self, painter, rect)


class FactoryScene(Scene):

    def __init__(self):
        super(FactoryScene, self).__init__()

    def initUI(self):
        self.grScene = FactoryGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)


class FactoryView(QWidget):

    def __init__(self, parent=None):
        super(FactoryView, self).__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scene = FactoryScene()
        self.grScene = self.scene.grScene
        self.view = QDMGraphicsView(self.grScene)

        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(self.view)

        self.node = FactoryNode(self.scene)

        sockethandler = FactorySocketHandler(self.node)
        sockethandler.socket_added.connect(self.node.grNode.adjust_socket_pos)
        highlighter = KelebekSyntaxHighlighter(sockethandler)
        options = FactoryNodeOptions(self.node)

        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(options)
        splitter2.addWidget(highlighter)
        splitter2.addWidget(sockethandler)
        splitter2.setStretchFactor(0, 1)
        splitter2.setStretchFactor(1, 4)
        splitter2.setStretchFactor(2, 10)
        splitter1.addWidget(splitter2)

        self.layout.addWidget(splitter1)
        highlighter.save_signal.connect(self.saveNode)
        highlighter.emit_eval.connect(self.saveNode)

        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)

    def eval_text(self, s):
        try:
            evaluation = eval(s)
            print(evaluation)
        except Exception as e:
            print("Exception:", e)

    def saveNode(self, s):
        custom_nodes = os.path.join(os.path.dirname(__file__), "customnodes")
        node_title = str(self.node.title) + '.json'
        new_node = custom_nodes + '/' + node_title

        ser_node = self.node.serialize()
        ser_node['shape'] = 'rounded rectangle'
        ser_node['operation'] = s
        print(ser_node)
        if node_title in os.listdir(custom_nodes):
            print('raise an alert dialog')
        else:
            with open(new_node, 'w') as file:
                file.write(json.dumps(ser_node, indent=4))

    def onDragEnter(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            event.setAccepted(False)

    def onDrop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream = QDataStream(eventData, QIODevice.ReadOnly)
            pixmap = QPixmap()
            dataStream >> pixmap
            op_code = dataStream.readInt()
            text = dataStream.readQString()

            mouse_position = event.pos()
            scene_position = self.grScene.views()[0].mapToScene(mouse_position)

            if DEBUG: print("GOT DROP: [%d] '%s'" % (op_code, text), "mouse:", mouse_position, "scene:", scene_position)

            try:
                node = get_class_from_opcode(op_code)(self.scene)
                node.setPos(scene_position.x(), scene_position.y())
                # self.history.storeHistory("Created node %s" % node.__class__.__name__)
            except Exception as e: dumpException(e)

            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()
