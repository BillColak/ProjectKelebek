from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class FactoryNodeOptions(QWidget):
    def __init__(self, node: 'Node', parent: QWidget = None):
        super().__init__(parent)
        self.node = node
        self.setLayout(QFormLayout())
        self.setContentsMargins(0,0,0,0)

        self.combo = QComboBox()
        self.combo.addItems(['rounded rectangle', 'cloud', 'circle', 'diamond', 'triangle'])

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

        self.node_color = QColorButton('Node Color')
        self.node_color.colorChanged.connect(self.change_nodecolor)

        form_fields = {
            'Title:': self.node_title,
            'Shape:': self.combo,
            # 'Sockets:': self.socketspinbox,
            'Socket Position': self.socket_posCombo,
            'Category': QLineEdit(),
            'Sub Category (Optional)': self.socket_pos,
            'Tooltip': QLineEdit('Enter node tooltip'),
            'node color': self.node_color,
        }
        for k, v in form_fields.items():
            self.layout().addRow(k, v)

    def socket_position(self):
        for socket in self.node.outputs:
            x, y = self.node.getSocketPosition(socket.index, socket.position, socket.count_on_this_node_side)
            print(x, y)

    # def socket_amount(self, s):
    #     x = [1 for i in range(int(s))]
    #     print(x)
    #     self.node.initSockets(x, [0], reset=False)  # make the rest false to append sockets vs remaking.

    def setNodeTitle(self, s):
        self.node.grNode.setTitle(s)

    def change_nodecolor(self, s):
        self.node.grNode.changeTitleColor(s)



class QColorButton(QPushButton):
    '''
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    '''

    colorChanged = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = None
        # self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(self._color)

        if self._color:
            # self.setStyleSheet("background-color: %s;" % self._color)
            self.setText(self._color)
        else:
            self.setStyleSheet("Color")

    def color(self):
        return self._color

    def onColorPicker(self):
        '''
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.

        '''
        dlg = QColorDialog(self)
        # if self._color:
        #     dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(None)

        return super(QColorButton, self).mousePressEvent(e)