from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from nodeeditor.node_scene import Scene
# from nodeeditor.node_graphics_scene import QDMGraphicsScene
from nodeeditor.node_graphics_view import QDMGraphicsView
from kelebek_node_base import KelebekNode
from kelebek_node_fab import FactoryNode
from kelebek_texteditor import MyHighlighter, KelebekSyntaxHighlighter
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

        highlighter = KelebekSyntaxHighlighter()
        sockethandler = FactorySocketHandler(self.node)
        options = FactoryNodeOptions(self.node)

        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(options)
        splitter2.addWidget(highlighter)
        splitter2.addWidget(sockethandler)

        # width = qApp.desktop().availableGeometry(self).width()
        # print(splitter2.width(), splitter1.width())
        # splitter2.setSizes([int(splitter2.width()*1/4), int(splitter2.width()*1/2), int(splitter2.width()*1/4)])
        # splitter2.saveState()
        splitter2.saveGeometry()
        # https://doc.qt.io/qt-5/qsplitter.html#saveState
        splitter1.addWidget(splitter2)

        self.layout.addWidget(splitter1)
        # self.layout.addWidget(self.view_layout)
