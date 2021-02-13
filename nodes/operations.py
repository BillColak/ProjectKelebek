
from PyQt5.QtCore import *
from kelebek_conf import *
from kelebek_node_base import *
from nodeeditor.utils import dumpException

from spider.kelebek_node_functions import get_item, multi_link, paginator
from kelebek_multithreading import run_threaded_process

import time
from colorama import Fore

import asyncio
# import requests
from requests import Session

DEBUG = True

# page_url = 'http://books.toscrape.com/'
# pagination_path = '//a[text()="next"]/@href'
# multi_title_path = '//h3/a/@href'

price_path = '//div[1]/div[2]/p[normalize-space(@class)="price_color"]/text()'
title_path = '//h1/text()'

# TODO all nodes with async which will made the app really clunky before multithreading so don't be disheartened.


# def xpath_root(page_source: str or bytes, base_url=None, parser=None) -> lxml_html.HtmlElement:
#     return lxml_html.fromstring(html=page_source, base_url=base_url, parser=parser)
#
#
# def get_first(list_elements):
#     try:
#         return list_elements.pop(0)
#     except:
#         return ''
#
#
# def get_item(resp, path):
#     return get_first(xpath_root(resp).xpath(path))
#
#
# def single_item(attributes: dict or None, path: str) -> str:
#     xpath_ = get_string_item(path)
#     if attributes:
#         attrib_xpath = [f'normalize-space(@{key})="{value.strip()}"' for key, value in attributes.items() if
#                         key != 'style']
#         if len(attrib_xpath) > 0:
#             return f'//{xpath_}[' + ' and '.join(attrib_xpath) + ']/text()'
#         else:
#             return f'//{xpath_}' + '/text()'
#     else:
#         return f'//{xpath_}' + '/text()'
#
#
# def get_string_item(value) -> str:
#     path = str(value).split('/')
#     if [i for i in ['table', 'tbody', 'tr', 'td'] if i in path]:
#         return "/".join(path[-3:])
#     else:
#         return "/".join(path[-3:-1]) + '/' + path[-1].split('[')[0]
#
#
# async def multi_link(loop: AbstractEventLoop, gen, path: str):
#     tasks = []
#     async with ClientSession(loop=loop) as session:
#         for i, j in enumerate(gen):
#             print(Fore.MAGENTA, f'Page-{i + 1}: ', j.url, flush=True)
#             urls = [urljoin(j.url, link) for link in xpath_root(j.content).xpath(path)]
#             for url in urls:
#                 tasks.append(loop.create_task(fetch(session, url)))
#
#         return await asyncio.gather(*tasks)
#
#         # for task in asyncio.as_completed(tasks):
#         #     earliest_result = await task
#         #     yield earliest_result
#
#
# async def fetch(session: ClientSession, url):
#     print(Fore.CYAN + f"FETCHING PAGES: {url}", flush=True)
#     async with session.get(url) as response:
#         response.raise_for_status()
#         html_body = await response.text()
#         return html_body


@register_node(OP_NODE_PAGINATION)
class KelebekNodePagination(KelebekNode):
    # icon = "icons/add.png"
    op_code = OP_NODE_PAGINATION
    op_title = "Pagination"
    content_label = ""
    content_label_objname = "Kelebek_node_pagination"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])

# TODO might need slot()s to catch this shit https://stackoverflow.com/questions/61842432/pyqt5-and-asyncio eventloop

    def evalOperation(self, input1_page, value1_pagination_path: str):
        print(Fore.RED, 'INPUT PAGE:', input1_page, flush=True)
        with Session() as client:
            for response in paginator(client, input1_page, value1_pagination_path):
                print(Fore.RED, f'Page-: ', response, flush=True)
                yield response
        # client.close()

    # def fetch(self, session: Session, url: str, path: str) -> requests.Response:
    #     resp = session.get(url)
    #     link = get_item(resp.content, path)
    #     yield resp
    #     if len(link) > 0:
    #         absolute_url = urljoin(url, link)
    #         yield from self.fetch(session, absolute_url, path)


@register_node(OP_NODE_HOP_LINK)
class KelebekNodeHopLink(KelebekNode):
    # icon = "icons/sub.png"
    op_code = OP_NODE_HOP_LINK
    op_title = "Hop Link"
    content_label = ""
    content_label_objname = "Kelebek_node_hop_link"

    def evalOperation(self, input1, value1):
        print(Fore.GREEN, 'HOP LINK: ', 'input1:', input1, 'value1:', value1, flush=True)
        if input1:
            return 'Hop Link: '+'input1:'+input1+'value1:'+value1
        else:
            return 'Hop Link: no input1: '+value1


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
        # for i in x:
        #     price = get_item(i, price_path)
        #     title = get_item(i, title_path)
        #     print(Fore.WHITE + f"BOOKS PRICE: {price} {title}", flush=True)


@register_node(OP_NODE_SINGLE_ITEM)
class KelebekNodeSingleItem(KelebekNode):
    # icon = "icons/sub.png"
    op_code = OP_NODE_SINGLE_ITEM
    op_title = "Get Item"
    content_label = ""
    content_label_objname = "Kelebek_node_single_item"

    def evalOperation(self, input1, value1):
        # print('INPUT1: ', next(input1))
        items = []
        for i in input1:
            item = get_item(i.content, value1)
            print(Fore.BLUE, 'ITEM: ', item)
            items.append(item)
        return items
        # items = [get_item(i.content, value1) for i in input1]
        #
        # print(Fore.BLUE, [get_item(i.content, value1) for i in input1])
        # return items  # could also use yield but is that useful for items?


@register_node(OP_NODE_MULTI_ITEM)
class KelebekNodeMultiItem(KelebekNode):
    # icon = "icons/sub.png"
    op_code = OP_NODE_MULTI_ITEM
    op_title = "Get All"
    content_label = ""
    content_label_objname = "Kelebek_node_multi_item"

    def evalOperation(self, input1, value1):
        print(Fore.GREEN, 'ALL ITEMS : ', 'input1:', input1, 'value1:', value1, flush=True)
        if input1:
            return 'ALL ITEMS: '+'input1:'+input1+'value1:'+value1
        else:
            return 'ALL ITEMS: no input1: '+value1


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

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = True
        self.output_multi_edged = True

    def update_progress(self, val):
        self.content.prg.setValue(val)

    def completed(self):
        print('COMPLETED')

    def print_output(self, s):
        print('OUTPUT: ', s)
        return s

    def execute_this_fn(self, val, progress_callback):
        for x in range(20, 101, 20):
            print(x)
            time.sleep(0.5)
            progress_callback.emit(x)
            self.value_output.append(x)
        return self.value_output

    def evalOperation(self, value1, *args):

        run_threaded_process(
            cb_func=self.execute_this_fn,
            progress_fn=self.update_progress,
            on_complete=self.completed,
            return_output=self.print_output,
        )

        return '123'
        # print(Fore.LIGHTCYAN_EX, 'TEST NODE: ', 'VALUE1:', value1, 'ARGS: ', args, flush=True)
        # print('ARGS: ', [i for i in args])
        # return 'TEST NODE: value1: '+value1+'ARGS: '+str(args)

    def evalImplementation(self):
        all_inputs_nodes = self.getInputs()
        v1 = self.content.edit.text()

        print(Fore.BLUE, 'ALL INPUT NODES: ', all_inputs_nodes, flush=True)
        # print(Fore.LIGHTGREEN_EX, 'ONE INPUT NODE: ', i1, type(i1), flush=True)

        if not all_inputs_nodes:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        else:
            # val = self.evalOperation(i1.eval(), v1)
            val = self.evalOperation(v1, *(node.eval() for node in all_inputs_nodes))  # so this is a gen expression

            self.value = val
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")

            self.markDescendantsDirty()
            self.evalChildren()

            return val


@register_node(OP_NODE_TEST_2)
class KelebekTestNode2(KelebekNode):
    op_code = OP_NODE_TEST_2
    op_title = "Test Node2"
    content_label = ""
    content_label_objname = "Kelebek_node_test2"

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = True
        self.output_multi_edged = True

    def evalOperation(self, value1, *args):
        print(Fore.LIGHTCYAN_EX, 'TEST NODE2: ', 'VALUE1:', value1, 'ARGS: ', args, flush=True)
        print('ARGS: ', [i for i in args])
        return 'TEST NODE2: value1: '+value1+'ARGS: '+str(args)

    def evalImplementation(self):
        all_inputs_nodes = self.getInputs()
        v1 = self.content.edit.text()

        print(Fore.BLUE, 'ALL INPUT NODES: ', all_inputs_nodes, flush=True)

        if not all_inputs_nodes:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        else:
            val = self.evalOperation(v1, *(node.eval() for node in all_inputs_nodes))

            self.value = val
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")

            self.markDescendantsDirty()
            self.evalChildren()

            return val


@register_node(OP_NODE_TEST_3)
class KelebekTestNode3(KelebekNode):
    op_code = OP_NODE_TEST_3
    op_title = "Test Node3"
    content_label = ""
    content_label_objname = "Kelebek_node_test3"

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = True
        self.output_multi_edged = True

    def evalOperation(self, value1, *args):
        print(Fore.LIGHTCYAN_EX, 'TEST NODE3: ', 'VALUE1:', value1, 'ARGS: ', args, flush=True)
        print('ARGS: ', [i for i in args])
        return 'TEST NODE3: value1: ' + value1 + 'ARGS: ' + str(args)

    def evalImplementation(self):
        all_inputs_nodes = self.getInputs()
        v1 = self.content.edit.text()

        print(Fore.BLUE, 'ALL INPUT NODES: ', all_inputs_nodes, flush=True)

        if not all_inputs_nodes:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        else:
            val = self.evalOperation(v1, *(node.eval() for node in all_inputs_nodes))

            self.value = val
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")

            self.markDescendantsDirty()
            self.evalChildren()

            return val


class KelebekTestNodeContent(KelebekContent):
    def initUI(self):
        self.contentlayout = QFormLayout(self)
        self.edit = QLineEdit("Enter XPath: ", self)
        self.edit.setAlignment(Qt.AlignLeft)
        self.contentlayout.addRow('XPath', self.edit)

        self.prg = QProgressBar()
        self.prg.setStyle(QStyleFactory.create("windows"))
        self.prg.setTextVisible(True)
        self.contentlayout.addRow(self.prg)


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


# way how to register by function call
# register_node_now(OP_NODE_ADD, CalcNode_Add)