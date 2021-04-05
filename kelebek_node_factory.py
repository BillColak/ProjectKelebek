from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from nodeeditor.node_scene import Scene
# from nodeeditor.node_graphics_scene import QDMGraphicsScene
from nodeeditor.node_graphics_view import QDMGraphicsView
from kelebek_node_base import KelebekNode
from kelebek_node_fab import FactoryNode
from syntaxhighlighter import MyHighlighter


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

        self.node = FactoryNode(self.scene)

        self.view_layout = QHBoxLayout()

        self.formlayoutSection()
        self.initTextEditor()
        self.initsocketSection()

        self.layout.addWidget(self.view)
        self.layout.addLayout(self.view_layout, Qt.AlignBottom)

    def initTextEditor(self):
        TextEditor_Layout = QVBoxLayout()
        self.node_operation = FactoryNodeOpTextEdit()

        eval_btn = QPushButton("eval")
        eval_btn.clicked.connect(self.evalEditorText)

        TextEditor_Layout.addWidget(self.node_operation)
        TextEditor_Layout.addWidget(eval_btn)

        self.view_layout.addLayout(TextEditor_Layout)

    def evalEditorText(self):
        text = self.node_operation.toPlainText()  # capture the white spaces as well
        print(text)
        # eval(text)

    def initsocketSection(self):
        self.socket_input = QWidget()
        self.socket_input.setContentsMargins(0,0,0,0)
        self.socket_input.setLayout(QVBoxLayout())

        self.add_socket = QPushButton(QIcon('icons/add.png'), "Add Socket", self.socket_input, clicked=self.insertSocket)
        self.add_socket.setStyleSheet("background-color: #00d100; color: #000000;")
        self.socket_input.layout().addWidget(self.add_socket, Qt.AlignTop)
        self.socket_input.layout().insertStretch(-1)
        self.view_layout.addWidget(self.socket_input)

    def formlayoutSection(self):
        self.combo = QComboBox()
        self.combo.addItems(['rounded rectangle'])

        self.slider_height = QSlider(Qt.Horizontal)

        self.operation = QLineEdit()
        self.operation.setPlaceholderText('type.. wanted node operation.')
        # self.socketspinbox = QSpinBox()
        # self.socketspinbox.textChanged.connect(self.socket_amount)

        self.socket_pos = QPushButton('Output Socket')
        self.socket_pos.clicked.connect(self.socket_position)
        self.socket_posCombo = QComboBox()
        self.socket_posCombo.addItems(['LEFT_TOP', 'LEFT_CENTER', 'LEFT_BOTTOM'])
        self.node_title = QLineEdit('Name Super Undefined')
        self.node_title.textChanged.connect(self.setNodeTitle)

        form_fields = {
            'Title:': self.node_title,
            'Shape:': self.combo,
            # 'Sockets:': self.socketspinbox,
            'Socket Position': self.socket_posCombo,
            'Category': QLineEdit(),
            'Sub Category (Optional)': self.socket_pos,
            'Tooltip': QLineEdit('Enter node tooltip')
        }

        self.formlay = QFormLayout()
        for k, v in form_fields.items():
            self.formlay.addRow(k, v)
        self.view_layout.addLayout(self.formlay)

    def socket_position(self):
        for socket in self.node.outputs:
            x, y = self.node.getSocketPosition(socket.index, socket.position, socket.count_on_this_node_side)
            print(x, y)

    def socket_amount(self, s):
        x = [1 for i in range(int(s))]
        print(x)
        self.node.initSockets(x, [0])  # make the rest false to append sockets vs remaking.

    def insertSocket(self):
        self.socket_input.layout().addWidget(SocketInput(self.node), Qt.AlignTop)

    def setNodeTitle(self, s):
        self.node.grNode.setTitle(s)


class SocketInput(QWidget):

    def __init__(self, node: 'Node', parent=None):
        super().__init__(parent)
        self.node = node
        # self.index
        # self.socket

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop)

        self.socket_name = QLineEdit()
        self.socket_name.setPlaceholderText('Optional: Enter Socket Name')

        self.socket_color = QPushButton('Socket Color')
        self.socket_color.clicked.connect(self.openColorDialog)

        self.remove = QToolButton()
        self.remove.setStyleSheet("background: #474747")
        self.remove.setIcon(QIcon("images/close_dark.png"))

        self.layout.addWidget(self.socket_name)
        self.layout.addWidget(self.socket_color)
        self.layout.addWidget(self.remove)

        self.remove.clicked.connect(self.removeMe)
        self.initSocket()

    def removeMe(self):
        self.setParent(None)
        self.deleteLater()

    def initSocket(self):
        pass
        # self.node.inputs.append(1)
        # self.node.initSockets(self.node.inputs, self.node.outputs)

        # socket = self.node.__class__.Socket_class(node=self, index=len(self.node.inputs), position=self.input_socket_position,
        #         socket_type=1, multi_edges=self.input_multi_edged,
        #         count_on_this_node_side=len(self.node.inputs), is_input=True
        #     )
        #
        # self.node.inputs.append(socket)

    #     counter = 0

    #     for item in inputs:
    #         socket = self.__class__.Socket_class(
    #             node=self, index=counter, position=self.input_socket_position,
    #             socket_type=item, multi_edges=self.input_multi_edged,
    #             count_on_this_node_side=len(inputs), is_input=True
    #         )
    #         counter += 1
    #         self.inputs.append(socket)

    @pyqtSlot()
    def openColorDialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print(color.name())


class FactoryNodeOpTextEdit(QTextEdit):
    def __init__(self, *args):
        super(FactoryNodeOpTextEdit, self).__init__(*args)
        highlighter = MyHighlighter(self, "Classic")

