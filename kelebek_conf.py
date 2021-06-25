from functools import reduce, partial


LISTBOX_MIMETYPE = "application/x-item"

OP_NODE_INPUT = 1
OP_NODE_STORE = 2
OP_NODE_TEST = 3
OP_NODE_RAND_NUM = 4
OP_NODE_PAGINATION = 6
OP_NODE_HOP_LINK = 7
OP_NODE_HOP_ALL_LINKS = 8
OP_NODE_SINGLE_ITEM = 9
OP_NODE_MULTI_ITEM = 10
OP_NODE_DISPLAY_OUTPUT = 11
CUSTOM_NODE = 12

KELEBEK_NODES = {
}

KELEBEK_NODES2 = {'Web Navigation': dict(),
                  'Item Extraction': dict(),
                  'Finance': {
                      'Financials': dict()
                  },
                  'Output': dict(),
                  'Factory Nodes': dict(),
                  }


class ConfException(Exception): pass
class InvalidNodeRegistration(ConfException): pass
class OpCodeNotRegistered(ConfException): pass


def register_node_now(class_reference):
    if isinstance(class_reference, partial):
        class_reference = class_reference.func

    category = class_reference.category
    if category:
        category_placement = deep_get(KELEBEK_NODES2, category)
        op_code = class_reference.op_code
        if category_placement.get(op_code):  # if already exists
            raise InvalidNodeRegistration("Duplicate node registration of '%s': '%s'. There is already %s" % (
                op_code, class_reference, KELEBEK_NODES[op_code]
            ))
        category_placement[op_code] = class_reference
        # if op_code < 12:
        KELEBEK_NODES[op_code] = class_reference
        # print(op_code, class_reference.op_title, class_reference.category, category_placement)


def register_node():
    def decorator(original_class):
        register_node_now(original_class)
        return original_class
    return decorator


def get_class_from_opcode(op_code):
    if op_code not in KELEBEK_NODES: raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return KELEBEK_NODES[op_code]


########
# def register_node_now2(op_code, parent, class_reference):
#     category = deep_get(KELEBEK_NODES2, parent)
#     if category is None:
#         raise InvalidNodeRegistration(f'Category Does Not Exist {category}')
#
#     if op_code in category:
#         raise InvalidNodeRegistration("Duplicate node registration of '%d'. There is already %d" % (
#             op_code, category[op_code]
#         ))
#     category[op_code] = class_reference
#     KELEBEK_NODES[op_code] = class_reference
#     print(op_code, class_reference.op_code)
#
#
# def register_node2(op_code, parent):
#     def decorator(original_class):
#         register_node_now2(op_code, parent, original_class)
#         return original_class
#     return decorator


def deep_get(dictionary, keys, default=None):
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictionary)


# import all nodes and register them
from nodes.input import *
from nodes.operations import *
from nodes.output import *
from nodes.custom_nodes import *
