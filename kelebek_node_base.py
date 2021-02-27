from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from nodeeditor.node_node import Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER
from nodeeditor.utils import dumpException

from colorama import Fore
# from WaitingSpinnerWidget import QtWaitingSpinner
from kelebek_multithreading import run_threaded_process
DEBUG = True


class KelebekGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 220
        self.height = 85
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def initAssets(self):
        super().initAssets()
        self.icons = QImage("icons/status_icons.png")

    # Mark Dirty, Invalid or Ok.
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )


class KelebekContent(QDMNodeContentWidget):
    def initUI(self):
        self.contentlayout = QFormLayout(self)
        self.edit = QLineEdit("Enter XPath", self)
        self.edit.setAlignment(Qt.AlignLeft)
        self.contentlayout.addRow('XPath', self.edit)
        # self.progressbar = QProgressBar()
        # self.progressbar.setRange(0, 1)
        # self.spinner = QtWaitingSpinner(self)

    # def submit(self):
    #     self.spinner.start()
    #     runnable = RequestRunnable(self)
    #     QThreadPool.globalInstance().start(runnable)
    #
    # @pyqtSlot(str)
    # def setData(self, data):
    #     print(data)
    #     self.spinner.stop()
    #     self.adjustSize()
        # self.spinner.adjustSize()

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


class KelebekNode(Node):
    icon = ""
    op_code = 0
    op_title = "Undefined"
    content_label = ""
    content_label_objname = "kelebek_node_bg"

    # GraphicsNode_class = KelebekGraphicsNode
    # NodeContent_class = KelebekContent

    def __init__(self, scene, inputs=[2], outputs=[1]):
        super().__init__(scene, self.__class__.op_title, inputs, outputs)
        self.value = None
        # self.value_output = []  # if the thread appends  to this. is it trying to access the widget?
        # The only way to learn this is by trying.
        # You are swimming in murky waters. Where sense of sight is useless. hence you have to adapt.

        # it's really important to mark all nodes Dirty by default
        self.markDirty()

    def initInnerClasses(self):
        self.content = KelebekContent(self)
        self.grNode = KelebekGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = False
        self.output_multi_edged = True

    # def receive(self):
    #     data = yield
    #     return data
    #
    # def deliver(self):
    #     pass

    def evalOperation(self, input1, input2):
        """ Node operations happen here, and given the output it gets evaluated and marked
        for all descending nodes."""
        # set some value ex: self.value_output = [],
        # .connect(self.eval) on signals.progress or results
        # return self.value_output
        return 123

    def evalImplementation(self):
        i1 = self.getInput(0)
        # op = self.getOutputs()
        v1 = self.content.edit.text()

        if i1 is None:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        else:

            val = self.evalOperation(i1.eval(), v1)
            self.value = val
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")

            # TODO read plan B in the Test Node and implement it.
            # if op is not None:
            #     while True:
            #         data = yield
            #         for i in op:
            #             i.send(data)

            self.markDescendantsDirty()
            self.evalChildren()

            return val

    def eval(self):
        # may also use eval children? which does not eval current node.children= one level below not all children
        if not self.isDirty() and not self.isInvalid():
            if DEBUG:
                print(Fore.MAGENTA, " _> returning cached %s value:" % self.__class__.__name__, self.value, flush=True)
            return self.value

        try:

            val = self.evalImplementation()
            return val
        except ValueError as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            self.markDescendantsDirty()
        except Exception as e:
            self.markInvalid()
            # self.markDescendantsInvalid() may want to also use this
            self.grNode.setToolTip(str(e))
            dumpException(e)

    def onInputChanged(self, socket=None):
        if DEBUG:
            print("%s::__onInputChanged" % self.__class__.__name__)
        self.markDirty()
        self.eval()

    # def onMarkedDirty(self):
    #     pass
    #
    # def onMarkedInvalid(self):
    #     pass

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        print("Deserialized KelebekNode '%s'" % self.__class__.__name__, "res:", res)
        return res
