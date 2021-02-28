
from PyQt5.QtCore import *
from kelebek_conf import *
from kelebek_node_base import *
from nodeeditor.utils import dumpException

# import time
import requests
# from colorama import Fore
# from collections import deque
# from kelebek_multithreading import run_threaded_process, DEFAULT_STYLE, COMPLETED_STYLE


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

    def get_page(self, page: str):  # make sure this returns just the url and not resp.
        resp = requests.get(page)
        if resp.ok:
            print("RESP OK! ")
            return page

    def initInnerClasses(self):
        self.content = KelebekInputContent(self)
        self.grNode = KelebekGraphicsNode(self)
        # self.content.edit.textChanged.connect(self.onInputChanged)  # if there is no eval overridden, then

    def evalImplementation(self):
        value1 = self.content.edit.text()

        # catching errors here allows for nodes to changes its states.
        # s_value = str(value1)
        # self.value = s_value

        resp = self.get_page(value1)
        self.value = resp

        self.running_thread = True
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()
        self.grNode.setToolTip("")
        self.evalChildren()

        return resp


class KelebekInputContent(KelebekContent):
    def initUI(self):
        self.contentlayout = QFormLayout(self)
        # self.edit = QLineEdit("Enter Information: ", self)
        self.edit = QLineEdit('http://books.toscrape.com/', self)
        self.edit.setAlignment(Qt.AlignLeft)
        self.contentlayout.addRow('URL', self.edit)

        # self.progressbar = QProgressBar()
        # self.progressbar.setStyleSheet(COMPLETED_STYLE)
        # self.progressbar.setTextVisible(False)
        # self.contentlayout.addRow(self.progressbar)
