from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from nodeeditor.node_node import Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER
from nodeeditor.utils import dumpException

from colorama import Fore
import inspect
from concurrent.futures import Future
# from WaitingSpinnerWidget import QtWaitingSpinner
from kelebek_multithreading import run_threaded_process, run_simple_thread
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
    running_thread = False

    def __init__(self, scene, inputs=[2], outputs=[1]):
        super().__init__(scene, self.__class__.op_title, inputs, outputs)
        self.value = None
        self.fut = Future()
        # self.fut.add_done_callback(self.finished)
        self.markDirty()

    def initInnerClasses(self):
        self.content = KelebekContent(self)
        self.grNode = KelebekGraphicsNode(self)
        # self.content.edit.textChanged.connect(self.onInputChanged)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = False
        self.output_multi_edged = True

    def finished(self, thread_result):
        self.running_thread = True
        self.fut.set_result(thread_result)
        self.value = thread_result
        print("THREAD FINISHED: ", thread_result)
        self.eval()
        get_all_outputs = self.getOutputs()
        for node in get_all_outputs:
            node.eval()
        # self.markDescendantsDirty(False)   #  --> instead fucking getoutputs().eval() # TODO the time it takes to do this is fucking sketchy

    def evalOperation(self, input1, input2):
        return 123

    def evalImplementation(self):
        i1 = self.getInput(0)
        v1 = self.content.edit.text()

        if i1 is None:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        elif not i1.running_thread:
            print('Is Thread running?', not i1.running_thread)
            self.grNode.setToolTip("Parent node has not finished operations")
            print(Fore.LIGHTBLACK_EX, 'Input: ', i1.eval())  # for some reason this is returning input as none
            # TODO if a connection is made while a thread is running, the input is none rather than a future.
            # if a thread is running a future must be returned
            # if a future is returned, than that future must be waited before continuing.
            # a signal should be sent to awaiting threads that future has completed.
            # set_running_or_notify_cancel()
            # onMarkedDirty(self) if input is future ait for future, then self.eval().

        else:
            if isinstance(i1.eval(), Future):
                print(Fore.BLACK, 'INPUT IS FUTURE')
                run_simple_thread(self.evalOperation, self.finished, i1.eval().result(), v1)
                # self.value = self.fut.result()
                return self.fut
            else:
                # here where the operation have completed before any connection or the input is not future...
                run_simple_thread(self.evalOperation, self.finished, i1.eval(), v1)
                # val = self.evalOperation(i1.eval(), v1)
                # self.value = val
                self.markDirty(False)
                self.markInvalid(False)
                self.grNode.setToolTip("")
                self.markDescendantsDirty()
                self.evalChildren()

                return self.fut

    def eval(self):
        print(Fore.YELLOW, '--> Eval Caller Name:', inspect.stack()[1][3])
        if not self.isDirty() and not self.isInvalid():
            if DEBUG:
                print(Fore.MAGENTA, " _> returning cached %s value:" % self.__class__.__name__, self.value, flush=True)
            return self.value

        try:
            val = self.evalImplementation()
            return val  # this means eval will always return a future.....

        except ValueError as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            self.markDescendantsDirty()
        except Exception as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            dumpException(e)

    def onInputChanged(self, socket=None):
        if DEBUG:
            print(Fore.BLUE, "%s::__onInputChanged" % self.__class__.__name__, 'Socket: ', socket)
        self.markDirty()
        self.eval()

    # def onMarkedDirty(self):
    #     pass  # could wait for future here
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
