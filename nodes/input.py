
from PyQt5.QtCore import *
from kelebek_conf import *
from kelebek_node_base import *
from nodeeditor.utils import dumpException

import time
import requests
from colorama import Fore
# from kelebek_multithreading import run_threaded_process


@register_node(OP_NODE_INPUT)
class KelebekNodeInput(KelebekNode):
    # icon = "icons/in.png"
    op_code = OP_NODE_INPUT
    op_title = "Start"
    content_label_objname = "Start_input_node"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.eval()
        # self.threadpool = QThreadPool()

    def get_page(self, page: str):  # make sure this returns just the url and not resp.
        resp = requests.get(page)
        if resp.ok:
            return page

    def print_output(self, s):
        print('OUTPUT: ', s)
        return s

    def initInnerClasses(self):
        self.content = KelebekInputContent(self)
        self.grNode = KelebekGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        value1 = self.content.edit.text()
        # s_value = str(value1)
        # self.value = s_value

        start_time = time.time()
        resp = self.get_page(value1)
        # run_threaded_process(
        #     threadpool=self.threadpool,
        #     cb_func=self.get_page,
        # )

        print(Fore.GREEN + 'Time: ', time.time() - start_time)
        self.value = resp

        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        return self.value


class KelebekInputContent(KelebekContent):
    def initUI(self):
        self.contentlayout = QFormLayout(self)
        self.edit = QLineEdit("Enter Information: ", self)
        self.edit.setAlignment(Qt.AlignLeft)
        self.contentlayout.addRow('URL', self.edit)
