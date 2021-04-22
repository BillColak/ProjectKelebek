
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# from nodeeditor.node_node import Node
from kelebek_node_base import KelebekNode
# from nodeeditor.node_content_widget import QDMNodeContentWidget
# from nodeeditor.node_graphics_node import QDMGraphicsNode
# from nodeeditor.utils import dumpException
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER, LEFT_TOP, LEFT_BOTTOM, RIGHT_TOP, RIGHT_BOTTOM

from kelebek_factory_graphics_node import ResizableNode
from colorama import Fore
# from kelebek_conf import register_node2, CUSTOM_NODE


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


# class FactoryNodeContent(QDMNodeContentWidget):
#     def initUI(self):
#         # self.node_op = QLabel('op', self)
#         self.contentlayout = QFormLayout(self)
#         self.edit = QLineEdit("Enter XPath", self)
#         self.edit.setAlignment(Qt.AlignLeft)
#         self.contentlayout.addRow('XPath', self.edit)
#
#     def serialize(self):
#         res = super().serialize()
#         res['value'] = self.edit.text()
#         return res
#
#     def deserialize(self, data, hashmap={}):
#         res = super().deserialize(data, hashmap)
#         try:
#             value = data['value']
#             self.edit.setText(value)
#             return True & res
#         except Exception as e:
#             dumpException(e)
#         return res


class FactoryNode(KelebekNode):
    icon = ""
    op_code = 12
    op_title = "Name Undefined"
    content_label = ""
    content_label_objname = "kelebek_node_bg"
    category = 'Factory Nodes'

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])

    def addSocket(self, socket):
        if socket.is_input:
            self.inputs.append(socket)
            self.named_inputs[self.inputs.index(socket)] = socket
        else:
            self.outputs.append(socket)
            self.named_outputs[self.outputs.index(socket)] = socket
        if isinstance(self.grNode, FactoryGraphicsNode):
            self.grNode.adjust_socket_pos()

    def getNamedInputs(self):
        ins = {}
        for name, socket in self.named_inputs.items():
            connections = ins[socket.name] = []
            for edge in socket.edges:
                other_socket = edge.getOtherSocket(socket)
                connections.append(other_socket.node)
        return ins

    def initInnerClasses(self):
        # self.content = FactoryNodeContent(self)
        self.grNode = FactoryGraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = True
        self.output_multi_edged = True

    def evalOperation(self, *args, **kwargs):
        print(Fore.BLUE, 'FACTORY INPUT:', args, kwargs)
        return args, kwargs

    def evalImplementation(self):
        i = {name: [i.eval() for i in node] for name, node in self.getNamedInputs().items()}
        x = self.evalOperation(**i)
        return x
        # ins = {}
        # for index, socket in enumerate(self.inputs):
        #     inp: list = [i.eval() for i in self.getInputs(index)]
        #     # todo if there is no name for more than one node this code will blow up.
        #     s_name: str = str(socket.name)
        #     ins[s_name] = inp
        # val = self.evalOperation(**ins)
        # return val

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        res['color'] = self.grNode.brush_title
        res['width'] = self.grNode.rect.width()
        res['height'] = self.grNode.rect.height()
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        pass


