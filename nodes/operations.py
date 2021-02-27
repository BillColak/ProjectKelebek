
from PyQt5.QtCore import *
from kelebek_conf import *
from kelebek_node_base import *
from nodeeditor.utils import dumpException

from spider.kelebek_node_functions import get_item, get_all, multi_link, paginator, broadcast, coroutine
from kelebek_multithreading import run_threaded_process, run_simple_thread

# import requests
# import time
from functools import partial
import os
from colorama import Fore

import asyncio
from requests import Session

DEBUG = True


# page_url = 'http://books.toscrape.com/'
# pagination_path = '//a[text()="next"]/@href'
# multi_title_path = '//h3/a/@href'

price_path = '//div[1]/div[2]/p[normalize-space(@class)="price_color"]/text()'
title_path = '//h1/text()'


@register_node(OP_NODE_HOP_LINK)
class KelebekNodeHopLink(KelebekNode):
    # icon = "icons/sub.png"
    op_code = OP_NODE_HOP_LINK
    op_title = "Hop Link"
    content_label = ""
    content_label_objname = "Kelebek_node_hop_link"

    def evalOperation(self, input1, value1):
        print("NOT IMPLEMENTED")


@register_node(OP_NODE_PAGINATION)
class KelebekNodePagination(KelebekNode):
    # icon = "icons/add.png"
    op_code = OP_NODE_PAGINATION
    op_title = "Pagination"
    content_label = ""
    content_label_objname = "Kelebek_node_pagination"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])

    def pagination(self, input1_page, value1_pagination_path: str):
        output = []
        print(Fore.CYAN, 'INPUT PAGE:', input1_page, flush=True)
        with Session() as client:
            for response in paginator(client, input1_page, value1_pagination_path, output):
                pass
            client.close()
        return output

    def evalOperation(self, input1_page, value1_pagination_path: str):
        return self.pagination(input1_page, value1_pagination_path)


@register_node(OP_NODE_HOP_ALL_LINKS)
class KelebekNodeHopAllLinks(KelebekNode):
    # icon = "icons/divide.png"
    op_code = OP_NODE_HOP_ALL_LINKS
    op_title = "Hop All Links"
    content_label = ""
    content_label_objname = "Kelebek_hop_all_links"

    def evalOperation(self, gen, path):
        loop = asyncio.get_event_loop()
        x = loop.run_until_complete(multi_link(loop, gen, path))
        return x


@register_node(OP_NODE_SINGLE_ITEM)
class KelebekNodeSingleItem(KelebekNode):
    # icon = "icons/sub.png"
    op_code = OP_NODE_SINGLE_ITEM
    op_title = "Get Item"
    content_label = ""
    content_label_objname = "Kelebek_node_single_item"

    # @coroutine
    def evalOperation(self, input1, value1):
        items = []
        for i in input1:
            item = get_item(i, value1)
            print(Fore.BLUE, 'ITEM: ', item)
            items.append(item)
        return items

        # output_nodes = self.getOutputs()
        # broadcaster = broadcast(output_nodes)
        # while True:
        #     data = yield

        # for i in input1:
        #     print(type(i))
        #     yield from get_item(i, value1)


@register_node(OP_NODE_MULTI_ITEM)
class KelebekNodeMultiItem(KelebekNode):
    # icon = "icons/sub.png"
    op_code = OP_NODE_MULTI_ITEM
    op_title = "Get All"
    content_label = ""
    content_label_objname = "Kelebek_node_multi_item"

    def get_all_items(self, input1, value1):
        output=[]
        for i in input1:
            output.append(get_all(i, value1))
        return output

    def evalOperation(self, input1, value1):
        return self.get_all_items(input1, value1)

        # output=[]
        # for i in input1:
        #     print(type(i))
        #     output.append(get_all(i, value1))
        # return output

        # This for iterating through TEST NODE one by one
        # for i in input1:
        #     items = get_all(i, value1)
        #     yield items

        # for i in input1:
        #     print(type(i))
        #     yield from get_all(i, value1)


@register_node(OP_NODE_DISPLAY_OUTPUT)
class KelebekNodeDisplayOutput(KelebekNode):
    # icon = "icons/sub.png"
    op_code = OP_NODE_DISPLAY_OUTPUT
    op_title = "Display Output"
    content_label = ""
    content_label_objname = "Kelebek_node_display_output"

    def initInnerClasses(self):
        self.content = KelebekOutputDisplayContent(self)
        self.grNode = KelebekDisplayGraphicsNode(self)
        # self.content.edit.textChanged.connect(self.onInputChanged)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = True
        self.output_multi_edged = True

    def evalOperation(self, *args):
        print(Fore.LIGHTBLACK_EX, 'OUTPUT ARGS: ', *args, flush=True)
        return 'DISPLAY NODE ARGS: '+str(args)

    def evalImplementation(self):
        all_inputs_nodes = self.getInputs()

        print(Fore.BLUE, 'ALL INPUT NODES: ', all_inputs_nodes, flush=True)

        if not all_inputs_nodes:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        else:
            val = self.evalOperation(*(node.eval() for node in all_inputs_nodes))

            self.value = val

            self.content.text_edit.setPlainText("%s" % val)
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")

            self.markDescendantsDirty()
            self.evalChildren()

            return val


@register_node(OP_NODE_TEST)
class KelebekTestNode(KelebekNode):
    op_code = OP_NODE_TEST
    op_title = "Test Node"
    content_label = ""
    content_label_objname = "Kelebek_node_test"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = True
        self.output_multi_edged = True

    def initInnerClasses(self):
        self.content = KelebekTestNodeContent(self)
        self.grNode = KelebekGraphicsNode(self)
        self.content.run_nodes.clicked.connect(self.clk_btn)

    def flatten(self, curr_item, output):
        import types
        if isinstance(curr_item, types.GeneratorType):
            for item in curr_item:
                self.flatten(item, output)
        else:
            output.append(curr_item)

    def clk_btn(self):
        all_inputs_nodes = self.getInputs()
        val = self.evalOperation(*(node.eval() for node in all_inputs_nodes))
        self.value = val

    def evalOperation(self, *args):
        print(Fore.GREEN, 'ARGS: ', args)
        # item_list = []
        # for arg in args:
        #     self.flatten(arg, item_list)
        #
        # print('Flatten length', len(item_list))

    def evalImplementation(self):
        all_inputs_nodes = self.getInputs()
        print(Fore.WHITE, 'ALL INPUT NODES: ', all_inputs_nodes, flush=True)

        if not all_inputs_nodes:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        # val = self.evalOperation(*(node.eval() for node in all_inputs_nodes))

        if self.value is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return

        self.markInvalid(False)
        self.markDirty(False)
        self.grNode.setToolTip("")

        return self.value


class KelebekTestNodeContent(QDMNodeContentWidget):
    def initUI(self):
        self.contentlayout = QFormLayout(self)
        self.run_nodes = QPushButton(QIcon(os.path.join('images', 'play-hot.png')), 'Run', self)
        self.contentlayout.addWidget(self.run_nodes)


class KelebekOutputDisplayContent(QDMNodeContentWidget):
    def initUI(self):
        self.display_layout = QVBoxLayout(self)
        self.text_edit = QPlainTextEdit('Placeholder text')
        self.text_edit.setStyleSheet("QPlainTextEdit {color: white}")
        self.text_edit.setFixedSize(200*2, 60*2)
        self.display_layout.addWidget(self.text_edit, alignment=Qt.AlignCenter)


class KelebekDisplayGraphicsNode(KelebekGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 220*2
        self.height = 85*2
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10
