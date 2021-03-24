
from PyQt5.QtCore import *
from kelebek_conf import *
from kelebek_node_base import *
from nodeeditor.utils import dumpException
from colorama import Fore


class KelebekStoreContent(QDMNodeContentWidget):
    def initUI(self):
        self.formlayout = QFormLayout(self)
        self.combo = QComboBox()
        self.combo.addItems(['CSV', 'DataBase', 'Text'])
        self.formlayout.addRow('Store as: ', self.combo)

    def serialize(self):
        res = super().serialize()
        res['combo'] = self.combo.currentIndex()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            combo = data['combo']
            self.combo.setCurrentIndex(combo)
            return True & res
        except Exception as e:
            dumpException(e)
        return res


@register_node2(OP_NODE_STORE, 'Output')
class KelebekNodeStore(KelebekNode):
    # icon = "icons/out.png"
    op_code = OP_NODE_STORE
    op_title = "Store Output"
    content_label_objname = "kelebek_node_store"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])

    def initInnerClasses(self):
        self.content = KelebekStoreContent(self)
        self.grNode = KelebekGraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = True

    def evalOperation(self, *args):
        print(Fore.LIGHTBLACK_EX, 'OUTPUT ARGS: ', *args, flush=True)
        return 'COLLECTED'

    def evalImplementation(self):
        all_inputs_nodes = self.getInputs()
        print(Fore.WHITE, 'ALL INPUT NODES: ', all_inputs_nodes, flush=True)

        if not all_inputs_nodes:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        # val = input_node.eval()
        val = self.evalOperation(*(node.eval() for node in all_inputs_nodes))  # dont need to do this unless have a legit operation.

        if val is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return

        # self.content.lbl.setText("%d" % val)
        # self.content.lbl.setText("%s" % val)
        self.markInvalid(False)
        self.markDirty(False)
        self.grNode.setToolTip("")

        return val
