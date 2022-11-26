from enum import IntEnum, auto


class NodeType(IntEnum):
    """Node type enum."""
    INPUT = auto()
    HIDDEN = auto()
    OUTPUT = auto()

class Task(IntEnum):
    CONNECTION_MUTATION = auto()
    NODE_MUTATION = auto()
    CONNECTION_UPDATE = auto()