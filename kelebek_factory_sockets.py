from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class SocketInput(QWidget):

    name_changed = pyqtSignal(str)

    def __init__(self, node: 'Node', parent=None):

        super().__init__(parent)

        self.node = node
        # self.grNode = self.node.grNode
        self.socket_type = '#ffaaff'
        self.name = ''
        self.socket = None
        self.index = len(self.node.inputs)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop)

        self.socket_name = QLineEdit()
        self.socket_name.setPlaceholderText('Enter Socket Name')
        self.socket_name.textChanged.connect(self.socket_name_changed)

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
        self.node.inputs.pop(self.index)
        self.node.scene.grScene.removeItem(self.socket.grSocket)
        self.setParent(None)
        self.deleteLater()

    def initSocket(self):
        inputs = [i for i in self.parent().children() if hasattr(i, 'socket_type')]
        if self.node.inputs:
            for socket in self.node.inputs:
                self.node.scene.grScene.removeItem(socket.grSocket)
            self.node.inputs = []

        counter = 0
        for item in inputs:
            self.socket = self.node.__class__.Socket_class(
                node=self.node, index=counter, position=self.node.input_socket_position,
                socket_type=item.socket_type, multi_edges=self.node.input_multi_edged,
                count_on_this_node_side=len(inputs), is_input=True, name=item.name
            )
            counter += 1
            self.node.inputs.append(self.socket)

    @pyqtSlot()
    def openColorDialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.socket_type = color.name()

            self.socket = self.node.inputs[self.index]
            self.socket.grSocket.socket_type = self.socket_type
            self.socket.grSocket.changeSocketType()

    def socket_name_changed(self, s):
        self.name = str(s)
        self.socket = self.node.inputs[self.index]
        self.socket.grSocket.setSocketTitle(str(s))


class FactorySocketHandler(QWidget):
    def __init__(self, node: 'Node', parent=None):
        super().__init__(parent)

        self.node = node

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(QVBoxLayout())

    def insertSocket(self):
        self.layout().addWidget(SocketInput(self.node, self), Qt.AlignTop)

    def getSocketsNameType(self):
        return [(i.name, i.socket_type) for i in self.children() if hasattr(i, 'socket_type')]



