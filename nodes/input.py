
from PyQt5.QtCore import *
from kelebek_conf import *
from kelebek_node_base import *
from nodeeditor.utils import dumpException

import time
# import requests
from colorama import Fore
# from collections import deque
from kelebek_multithreading import run_threaded_process


@register_node(OP_NODE_INPUT)
class KelebekNodeInput(KelebekNode):
    # icon = "icons/in.png"
    op_code = OP_NODE_INPUT
    op_title = "Start"
    content_label_objname = "Start_input_node"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.eval()
        self.value_output = []
        # self.VAL = []

    # def get_page(self, page: str):  # make sure this returns just the url and not resp.
    #     resp = requests.get(page)
    #     # progress_callback.emit(resp)
    #     if resp.ok:
    #         return page

    def initInnerClasses(self):
        self.content = KelebekInputContent(self)
        self.grNode = KelebekGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)  # if there is no eval overridden, then

        # evalImplementation is basically called.
        # self.content.edit.textChanged.connect(partial(
        # self.run_threaded_process, self.threadpool, self.get_page, self.etc))

    def update_progress(self, val):
        self.content.prg.setValue(val)

    def completed(self):
        print('COMPLETED')

    def print_output(self, s):
        print('OUTPUT: ', s)
        return s

    def execute_this_fn(self, progress_callback):
        for x in range(20, 101, 5):
            print(x)
            time.sleep(0.5)
            progress_callback.emit(x)
            self.value_output.append(x)
        return self.value_output

    def evalImplementation(self):
        value1 = self.content.edit.text()
        # s_value = str(value1)
        # self.value = s_value

        run_threaded_process(
            cb_func=self.execute_this_fn,
            progress_fn=self.update_progress,
            on_complete=self.completed,
            return_output=self.print_output,
        )

        # start_time = time.time()
        # resp = self.get_page(value1)
        # print(Fore.GREEN + 'Time: ', time.time() - start_time)
        # self.value = resp

        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        return self.value_output


class KelebekInputContent(KelebekContent):
    def initUI(self):
        self.contentlayout = QFormLayout(self)
        self.edit = QLineEdit("Enter Information: ", self)
        self.edit.setAlignment(Qt.AlignLeft)
        self.contentlayout.addRow('URL', self.edit)
        self.prg = QProgressBar()
        self.prg.setStyle(QStyleFactory.create("windows"))
        self.prg.setTextVisible(True)
        self.contentlayout.addRow(self.prg)
