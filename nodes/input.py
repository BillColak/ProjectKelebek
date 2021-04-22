
from PyQt5.QtCore import *
from kelebek_conf import register_node
from kelebek_node_base import *

import requests


@register_node()
class KelebekNodeInput(KelebekNode):
    # icon = "icons/in.png"
    op_code = 1
    op_title = "Start"
    content_label_objname = "Start_input_node"
    category = "Web Navigation"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.eval()
        self.value_output = []
        # self.VAL = []

    def get_page(self, page: str):  # make sure this returns just the url and not resp.
        resp = requests.get(page)
        if resp.ok:
            print("RESP OK! ")
            return resp

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
