from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class SocketInput(QWidget):

    def __init__(self, node: 'Node', parent=None):
        super().__init__(parent)
        self.node = node
        self.socket_type = '#ffaaff'
        self.socket = None

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
        x = [i.socket_type for i in self.parent().children() if hasattr(i, 'socket_type')]
        self.node.initSockets(x, [1])

    @pyqtSlot()
    def openColorDialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print(color.name())
            self.socket_type = color.name()


class FactorySocketHandler(QWidget):
    def __init__(self, node: 'Node', parent=None):
        super().__init__(parent)
        self.node = node

        self.setContentsMargins(0,0,0,0)
        self.setLayout(QVBoxLayout())

        self.add_socket = QPushButton(QIcon('icons/add.png'), "Add Socket", self, clicked=self.insertSocket)
        self.add_socket.setStyleSheet("background-color: #00d100; color: #000000;")
        self.layout().addWidget(self.add_socket, Qt.AlignTop)
        self.layout().insertStretch(-1)

    def insertSocket(self):
        self.layout().addWidget(SocketInput(self.node, self), Qt.AlignTop)


