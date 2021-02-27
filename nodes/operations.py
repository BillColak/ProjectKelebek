
from PyQt5.QtCore import *
from kelebek_conf import *
from kelebek_node_base import *
from nodeeditor.utils import dumpException

from spider.kelebek_node_functions import get_item, get_all, multi_link, paginator, broadcast, coroutine
from kelebek_multithreading import run_threaded_process, DEFAULT_STYLE, COMPLETED_STYLE

# import requests
# import time
import os
from colorama import Fore

import asyncio
from requests import Session

DEBUG = True

# TODO Coding Standards, all returned/(yielded) items must be generators.
# The yielded generators should all be lists unless other wise stated?

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
        print(Fore.CYAN, 'INPUT PAGE:', input1_page, flush=True)
        with Session() as client:
            for response in paginator(client, input1_page, value1_pagination_path):
                yield response
        client.close()

    # @coroutine
    def evalOperation(self, input1_page, value1_pagination_path: str):
        # output_nodes = self.getOutputs()
        # broadcaster = broadcast(output_nodes)
        # while True:
        #     data = yield  # when this is where you make a connection to this node.
        #     output = self.pagination(data, value1)  # it no
        #     broadcaster.send(output)
        output_nodes = self.getOutputs()
        print(Fore.CYAN, 'INPUT PAGE:', input1_page, flush=True)
        with Session() as client:
            for response in paginator(client, input1_page, value1_pagination_path):
                yield response
        client.close()


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

    def evalOperation(self, input1, value1):
        # This for iterating through TEST NODE one by one
        # for i in input1:
        #     items = get_all(i, value1)
        #     yield items

        output=[]
        for i in input1:
            print(type(i))
            output.append(get_all(i, value1))
        return output

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
        # tODO find a different function to run or make another todo make tool tips for listbox items, don't know wtf
        #  any of these nodes do. (include if it allows for 1> connections)
        #  if allows for 1> args upload to list?,
        #  cyclic iterator is infinite, put time on it.
        #  if it allows for multiple outputs which is every fucking node, use itertools.cycle.
        #  Or find out how many outputs a node has and make copies of the generators.
        #  Or make a delegators that acts as a transistors where it will call the node when requested but turns the
        #  generators to a list. allowing for multiple iterations
        # TODO yield the same thing n (output connection) amout of times.


        # TODO Plan B make changes to EvalImplementaion so that it has three parts: receive, calculation, send. where
        #  marked dirty if not EvalOperation, Also DONT FUCKING PUT ANYTHING IN EVALOP OTHER THAN THE OPERATION.
        self.value = val

    def evalOperation(self, *args):
        print(Fore.BLUE, 'ARGS: ', args)
        # item_list = []
        # for i in args:
        #     resp = next(i)
        #     print(resp)
            # self.flatten(i, item_list)
        #
        # for i, j in enumerate(item_list):
        #     print(f"Item-{i+1}: ", j)
        # print('Flatten length', len(item_list))
        # return item_list

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
