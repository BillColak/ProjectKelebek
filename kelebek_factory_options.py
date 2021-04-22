from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class FactoryNodeOptions(QWidget):

    def __init__(self, node: 'Node', parent: QWidget = None):
        super().__init__(parent)
        self.node = node
        self.setLayout(QFormLayout())
        self.setContentsMargins(0, 0, 0, 0)

        # self.combo = QComboBox()
        # self.combo.addItems(['rounded rectangle', 'cloud', 'circle', 'diamond', 'triangle'])
        #
        # self.socket_posCombo = QComboBox()
        # self.socket_posCombo.addItems(['LEFT_TOP', 'LEFT_CENTER', 'LEFT_BOTTOM'])

        self.node_color = QColorButton('Node Color')
        self.node_color.colorChanged.connect(self.change_nodecolor)

        self.node_title = QLineEdit('Undefined')
        self.node_title.textChanged.connect(self.setNodeTitle)

        self.node_shape = QLineEdit()
        self.category = QLineEdit()
        self.tool_tip = QLineEdit()
        # self.node_color = QLineEdit()

        form_fields = {
            'Title:': self.node_title,
            'Shape:': self.node_shape,
            'Category': self.category,
            'Tooltip': self.tool_tip,
            'node color': self.node_color,
        }
        for k, v in form_fields.items():
            self.layout().addRow(k, v)

    def setNodeTitle(self, s):
        self.node.title = s
        # self.node.__class__.op_title = s
        # self.node.grNode.setTitle(s)

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