
from PyQt5.QtCore import *
from kelebek_conf import *
from kelebek_node_base import *
from nodeeditor.utils import dumpException

from spider.kelebek_node_functions import get_item, get_all, multi_link, paginator, refactor_path_pagination_xpath,\
    refactor_path_single_link, refactor_path_multi_link, refactor_path_single_item, refactor_path_multi_item, single_link

import os
from colorama import Fore

import asyncio
from requests import Session
from concurrent.futures import Future

DEBUG = True

# TODO can make it so it is not possible for non-connection(nodes that return string) to be the input of connection
#  nodes. When a thread is running and an edge is being moved around without a connection.
#  the node thinks it has a connection there for ask for outputs when there is none.

# page_url = 'http://books.toscrape.com/'
# pagination_path = '//a[text()="next"]/@href'
# multi_title_link_path = '//h3/a/@href'

price_path = '//div[1]/div[2]/p[normalize-space(@class)="price_color"]/text()'
title_path = '//h1/text()'
star_rating = "//*[contains(@class, 'star-rating')]/@class"
product_description = "//*[@id='product_description']/following-sibling::p/text()"


@register_node2(OP_NODE_PAGINATION, 'Web Navigation')
class KelebekNodePagination(KelebekNode):
    icon = "icons/add.png"
    op_code = OP_NODE_PAGINATION
    op_title = "Pagination"
    content_label = ""
    content_label_objname = "Kelebek_node_pagination"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])

    def xpath_operation(self, **kwargs) -> str:
        text_value = kwargs.get('text')
        path = kwargs.get('xpath')
        attributes = kwargs.get('attributes')
        return refactor_path_pagination_xpath(text_value, path, attributes)

    def pagination(self, input1_page, value1_pagination_path: str):
        output = []
        print(Fore.CYAN, 'INPUT PAGE:', input1_page, flush=True)
        with Session() as client:
            for response in paginator(client, input1_page, value1_pagination_path, output):
                # time.sleep(1)
                pass
            client.close()
        return output

    def evalOperation(self, input1_page, value1_pagination_path: str):
        if isinstance(input1_page, Future):
            input1_page = input1_page.result()
            print('input is a future')
        x = self.pagination(input1_page, value1_pagination_path)
        return x


@register_node2(OP_NODE_HOP_ALL_LINKS, 'Web Navigation')
class KelebekNodeHopAllLinks(KelebekNode):
    # icon = "icons/divide.png"
    op_code = OP_NODE_HOP_ALL_LINKS
    op_title = "Hop All Links"
    content_label = ""
    content_label_objname = "Kelebek_hop_all_links"

    def xpath_operation(self, **kwargs) -> str:
        path = kwargs.get('xpath')
        attributes = kwargs.get('attributes')
        return refactor_path_multi_link(path, attributes)

    def evalOperation(self, gen, path):
        if isinstance(gen, Future):
            gen = gen.result()

        new_loop = asyncio.new_event_loop()
        x = new_loop.run_until_complete(multi_link(new_loop, gen, path))  # todo make sure this never call the same
        # coroutine twice? check the docs.

        self.running_thread = True
        return x


@register_node2(OP_NODE_HOP_LINK, 'Web Navigation')
class KelebekNodeHopLink(KelebekNode):
    # icon = "icons/sub.png"
    op_code = OP_NODE_HOP_LINK
    op_title = "Hop Link"
    content_label = ""
    content_label_objname = "Kelebek_node_hop_link"

    def xpath_operation(self, **kwargs) -> str:
        path = kwargs.get('xpath')
        attributes = kwargs.get('attributes')
        return refactor_path_single_link(path, attributes)

    def evalOperation(self, input1, value1):
        if isinstance(input1, Future):
            input1 = input1.result()
            print('input is a future')

        items = []
        for i in input1:
            item = get_item(i, value1)
            link = single_link(item)
            print(Fore.BLUE, 'LINK: ', link.url)
            items.append(link)
        self.running_thread = True
        return items


@register_node2(OP_NODE_SINGLE_ITEM, 'Item Extraction')
class KelebekNodeSingleItem(KelebekNode):
    # icon = "icons/sub.png"
    op_code = OP_NODE_SINGLE_ITEM
    op_title = "Get Item"
    content_label = ""
    content_label_objname = "Kelebek_node_single_item"

    def xpath_operation(self, **kwargs) -> str:
        path = kwargs.get('xpath')
        attributes = kwargs.get('attributes')
        return refactor_path_single_item(path, attributes)

    def evalOperation(self, input1, value1):
        if isinstance(input1, Future):
            input1 = input1.result()
            print('input is a future')

        items = []
        for i in input1:
            item = get_item(i, value1)
            print(Fore.BLUE, 'ITEM: ', item)
            items.append(item)
        self.running_thread = True
        return items


@register_node2(OP_NODE_MULTI_ITEM, 'Item Extraction')
class KelebekNodeMultiItem(KelebekNode):
    # icon = "icons/sub.png"
    op_code = OP_NODE_MULTI_ITEM
    op_title = "Get All"
    content_label = ""
    content_label_objname = "Kelebek_node_multi_item"

    def xpath_operation(self, **kwargs) -> str:
        path = kwargs.get('xpath')
        attributes = kwargs.get('attributes')
        return refactor_path_multi_item(path, attributes)

    def get_all_items(self, input1, value1):
        if isinstance(input1, Future):
            input1 = input1.result()
            print('input is a future')

        output = []
        for i in input1:
            output.append(get_all(i, value1))
        self.running_thread = True
        return output

    def evalOperation(self, input1, value1):
        return self.get_all_items(input1, value1)


@register_node2(OP_NODE_DISPLAY_OUTPUT, 'Web Navigation')
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
        self.running_thread = True
        return args

    def evalImplementation(self):
        all_inputs_nodes = self.getInputs()

        print(Fore.BLUE, 'ALL INPUT NODES: ', all_inputs_nodes, flush=True)

        if not all_inputs_nodes:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None  # because of this (same thing in the node base), the display thinks its inputs are none.
            # this is wrong as the new coding standards indicate that future should be returned. BUT.
            # if this is the case how do you evaluate this. and provide feedback to the user.
            # would have to provide a custom future object which indicates that its own
            # input is also waiting on something or does not have an input. hence it is none.
            # ^is there a way to get around this with qt threads and signals?

        else:
            val = self.evalOperation(*(node.eval() for node in all_inputs_nodes))
            print('Display val: ', val)

            self.value = val

            self.content.text_edit.setPlainText("%s" % str(val))
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")

            self.markDescendantsDirty()
            self.evalChildren()

            return val


@register_node2(OP_NODE_TEST, 'Finance.Financials')
class KelebekTestNode(KelebekNode):
    icon = "icons/sub.png"
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

    def clk_btn(self):
        all_inputs_nodes = self.getInputs()
        val = self.evalOperation(*(node.eval() for node in all_inputs_nodes))
        self.value = val
        self.eval()

    def evalOperation(self, *args):
        for arg in args:
            if isinstance(arg, Future):
                arg = arg.result()
            print(Fore.GREEN, 'ARG LENGTH: ', len(arg))
            print(Fore.GREEN, 'ARG: ', arg)
        x = [i for i in args]
        return x

    def evalImplementation(self):
        all_inputs_nodes = self.getInputs()
        if not all_inputs_nodes:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        # val = self.evalOperation(*(node.eval() for node in all_inputs_nodes))

        if self.value is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return

        # self.value = val
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
