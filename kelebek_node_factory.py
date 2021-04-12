import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from nodeeditor.node_scene import Scene
from nodeeditor.node_graphics_view import QDMGraphicsView
# from nodeeditor.node_graphics_scene import QDMGraphicsScene
# from kelebek_node_base import KelebekNode
from kelebek_factory_node import FactoryNode
from kelebek_texteditor import KelebekSyntaxHighlighter
from kelebek_factory_sockets import FactorySocketHandler
from kelebek_factory_options import FactoryNodeOptions


class FactoryGraphicsScene(QGraphicsScene):
    """Class representing Graphic of :class:`~nodeeditor.node_scene.Scene`"""

    #: pyqtSignal emitted when some item is selected in the `Scene`
    itemSelected = pyqtSignal()

    #: pyqtSignal emitted when items are deselected in the `Scene`
    itemsDeselected = pyqtSignal()

    def __init__(self, scene:'Scene', parent:QWidget=None):
        """
        :param scene: reference to the :class:`~nodeeditor.node_scene.Scene`
        :type scene: :class:`~nodeeditor.node_scene.Scene`
        :param parent: parent widget
        :type parent: QWidget
        """
        super().__init__(parent)

        self.scene = scene
        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        # settings
        self.gridSize = 20
        self.gridSquares = 5

        self.initAssets()
        self.setBackgroundBrush(self._color_background)

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._color_background = QColor("#A0A0A0")
        self._font_state = QFont("Ubuntu", 16)
        self._font_state.setStyleStrategy(QFont.PreferAntialias)

    # the drag events won't be allowed until dragMoveEvent is overriden
    def dragMoveEvent(self, event):
        """Overriden Qt's dragMoveEvent to enable Qt's Drag Events"""
        pass

    def setGrScene(self, width:int, height:int):
        """Set `width` and `height` of the `Graphics Scene`"""
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter:QPainter, rect:QRect):
        """Draw background scene grid"""
        super().drawBackground(painter, rect)


class FactoryScene(Scene):

    def __init__(self):
        super(FactoryScene, self).__init__()

    def initUI(self):
        """Set up Graphics Scene Instance with FactoryGraphicsScene instead"""
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
        highlighter = KelebekSyntaxHighlighter(sockethandler)
        options = FactoryNodeOptions(self.node)

        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(options)
        splitter2.addWidget(highlighter)
        splitter2.addWidget(sockethandler)
        splitter2.saveGeometry()
        splitter1.addWidget(splitter2)

        self.layout.addWidget(splitter1)
        highlighter.save_signal.connect(self.saveNode)
        highlighter.emit_eval.connect(self.saveNode)

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
