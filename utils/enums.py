from enum import Enum


class NodeType(Enum):
    """Node type enum."""
    INPUT = 1
    HIDDEN = 2
    OUTPUT = 3

class Task(Enum):
    CONNECTION_MUTATION = 1
    NODE_MUTATION = 2
    CONNECTION_UPDATE = 4