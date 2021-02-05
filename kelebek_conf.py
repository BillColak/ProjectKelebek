LISTBOX_MIMETYPE = "application/x-item"

OP_NODE_INPUT = 1
OP_NODE_STORE = 2
OP_NODE_PAGINATION = 3
OP_NODE_HOP_LINK = 4
OP_NODE_HOP_ALL_LINKS = 5
OP_NODE_TEST = 6
OP_NODE_SINGLE_ITEM = 7
OP_NODE_MULTI_ITEM = 8
OP_NODE_DISPLAY_OUTPUT = 9

# OP_NODE_IMAGE = 7
# OP_NODE_SPECIAL_INPUT = 8


KELEBEK_NODES = {
}


class ConfException(Exception): pass
class InvalidNodeRegistration(ConfException): pass
class OpCodeNotRegistered(ConfException): pass


def register_node_now(op_code, class_reference):
    if op_code in KELEBEK_NODES:
        raise InvalidNodeRegistration("Duplicate node registration of '%s'. There is already %s" %(
            op_code, KELEBEK_NODES[op_code]
        ))
    KELEBEK_NODES[op_code] = class_reference


def register_node(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class
    return decorator

def get_class_from_opcode(op_code):
    if op_code not in KELEBEK_NODES: raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return KELEBEK_NODES[op_code]



# import all nodes and register them
from nodes import *