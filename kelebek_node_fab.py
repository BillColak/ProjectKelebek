
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from nodeeditor.node_node import Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.utils import dumpException
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER, LEFT_TOP, LEFT_BOTTOM, RIGHT_TOP, RIGHT_BOTTOM

from kelebek_factory_node import ResizableNode


class FactoryGraphicsNode(ResizableNode):
    def initSizes(self):
        super().initSizes()
        self.width = self.rect.width()
        self.height = self.rect.height()
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def initAssets(self):
        super().initAssets()
        self.icons = QImage("icons/status_icons.png")

    # Mark Dirty, Invalid or Ok.
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, option, widget)

        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )


class FactoryNodeContent(QDMNodeContentWidget):
    def initUI(self):
        self.contentlayout = QFormLayout(self)
        self.edit = QLineEdit("Enter XPath", self)
        self.edit.setAlignment(Qt.AlignLeft)
        self.contentlayout.addRow('XPath', self.edit)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res


class FactoryNode(Node):
    icon = ""
    op_code = 0
    op_title = "Name Undefined"
    content_label = ""
    content_label_objname = "kelebek_node_bg"

    def __init__(self, scene, inputs=[], outputs=[1]):
        super().__init__(scene, self.__class__.op_title, inputs, outputs)

    def initInnerClasses(self):
        # self.content = FactoryNodeContent(self)
        self.grNode = FactoryGraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = False
        self.output_multi_edged = True

    def evalOperation(self, input1, input2):
        return 123

    def evalImplementation(self):
        pass

    def eval(self, index=0):
        pass

    def onInputChanged(self, socket=None):
        pass

    def serialize(self):
        pass

    def deserialize(self, data, hashmap={}, restore_id=True):
        pass



