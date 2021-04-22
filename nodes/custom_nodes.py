import os
from pathlib import Path
import json
from kelebek_node_base import KelebekNode, KelebekGraphicsNode
from nodeeditor.utils import dumpException

from kelebek_conf import register_node

e = os.path.join(Path(__file__).parent.parent, 'customnodes')
custom_nodes = [os.path.join(e, i) for i in os.listdir(e)]


class InvalidFile(Exception): pass


class CustomGraphicsNode(KelebekGraphicsNode):

    def initSizes(self):
        super().initSizes()
        self.width = self.node.width
        self.height = self.node.height
        self.edge_roundness = 6
        self.edge_padding = 10
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10


class CustomNode(KelebekNode):
    # icon = "icons/add.png"
    op_code = 12
    op_title = "Custom Node"
    content_label = ""
    content_label_objname = "Kelebek_node_custom"
    category = 'Factory Nodes'

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        for sock in self.input_sockets:
            socket = self.__class__.Socket_class(
                        node=self, position=self.input_socket_position,
                        socket_type=sock['socket_type'], multi_edges=self.input_multi_edged,
                        count_on_this_node_side=len(self.inputs)+1, is_input=True, name=sock['socket_name']
                    )
            self.addSocket(socket)

    def initInnerClasses(self):
        # self.content = KelebekContent(self)
        self.grNode = CustomGraphicsNode(self)
        # self.content.edit.textChanged.connect(self.onInputChanged)

    def initSettings(self):
        super().initSettings()
        self.input_multi_edged = True
        self.output_multi_edged = True

    def testfunc(self, x, y):
        return x*y

    def evalOperation(self, *args, **kwargs):
        one = kwargs.get('one')
        two = kwargs.get('two')
        out = list(map(self.testfunc, one, two))

        print('Operation: ', self.operation, 'args: ', args, 'kwargs: ', kwargs, out)
        return out

    def evalImplementation(self):
        # todo only accepts(edge connections) with predetermined types of inputs? int, str, etc..?
        # i = {name: node for name, node in self.getNamedInputs().items()} # --> show socket name + connections.
        i = {name: [i.eval() for i in node] for name, node in self.getNamedInputs().items()}
        x = self.evalOperation(**i)
        return x


def loadFromFile(filename: str):
    with open(filename, "r") as file:
        raw_data = file.read()
        try:
            data = json.loads(raw_data)
            return data
        except json.JSONDecodeError:
            raise InvalidFile("%s is not a valid JSON file" % os.path.basename(filename))
        except Exception as e:
            dumpException(e)


# todo make this into a decorator?
def factory(BaseClass, data, op_code):
    class NewClass(BaseClass): pass
    for key, item in data.items():
        if str(key) not in ['id', 'pos_x', 'pos_y', 'content', 'inputs', 'outputs']:
            setattr(NewClass, str(key), item)
        setattr(NewClass, 'input_sockets', data['inputs'])
        setattr(NewClass, 'output_sockets', data['outputs'])
        setattr(NewClass, 'op_code', op_code)
        setattr(NewClass, 'op_title', data['title'])
    return NewClass


o = 12
for item in custom_nodes:
    data_ = loadFromFile(item)
    custom_node = factory(CustomNode, data_, o)
    register_node()(custom_node)
    o += 12

