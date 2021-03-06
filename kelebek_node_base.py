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
from kelebek_multithreading import run_simple_thread
DEBUG = False


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
        # TODO Future exceptions.
        # TODO if xpath is not valid. User should click eval after confirming.->remove the marking shit from contextmenu
        # TODO revamp eval as it is not providing useful tooltips.

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
        print("THREAD FINISHED: ")
        self.eval()
        get_all_outputs = self.getOutputs()
        for node in get_all_outputs:
            node.eval()

    def evalOperation(self, input1, input2):
        return 123

    def evalImplementation(self):
        i1 = self.getInput(0)
        v1 = self.content.edit.text()
        # self.content.edit.setText()

        if i1 is None:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        elif not i1.running_thread:
            print('Is Thread running?', not i1.running_thread)
            self.grNode.setToolTip("Parent node has not finished operations")
            print(Fore.LIGHTBLACK_EX, 'Input: ', i1.eval())  # for some reason this is returning input as none
            #  if a connection is made while a thread is running, the input is none rather than a future.
            #  for interactivity during background operation specifically async functions, wait_for(wrap_future())
            #  but have it in the base node because apperanly you can get one page with
            #  aiohhtp, aiohttp.request('GET', url), because the end goal is to convert all functions to async/ or gen?
            # can also use dbeazley's from_coroutine functions to mix sync async functions?

            # if a thread is running a future must be returned
            # if a future is returned, than that future must be waited before continuing.
            # a signal should be sent to awaiting threads that future has completed.
            # set_running_or_notify_cancel()
            # onMarkedDirty(self) if input is future ait for future, then self.eval().
            # future = asyncio.run_coroutine_threadsafe(coro_func(), loop)
            # https://docs.python.org/3/library/asyncio-dev.html#asyncio-multithreading

            # the app the is freezing up at the point of making an edge connection with a socket. --> Because it goes
            # to thread and then back -> rinse n repeat. Is it possible to have all the back ground operations in a
            # different thread? most likely do to transfer of huge memory files. Generators will have to be
            # implemented to fix this.
            # https://hackernoon.com/threaded-asynchronous-magic-and-how-to-wield-it-bba9ed602c32

        else:
            if isinstance(i1.eval(), Future):
                print(Fore.BLACK, 'INPUT IS FUTURE')
                run_simple_thread(self.evalOperation, self.finished, i1.eval().result(), v1)
                # self.value = self.fut.result()
                return self.fut
            else:
                # here where the operation have completed before any connection or the input is not future...
                # if generators are re implemented, calling next(i.eval()) here instead of having for loops
                # in each node operations makes sense. also await wait_for(wrap_future(fut), None) generator.
                # if future fails during scraping loop.create_future() = new_future
                # add_done_callback(callback, *, context=None) -- can always use this, but u have to use partial?
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
        print(Fore.YELLOW, '--> Eval Caller Name:', inspect.stack()[1][3], ', Node Name:', self)
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
