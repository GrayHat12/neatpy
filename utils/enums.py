from enum import Enum


class NodeType(Enum):
    """Node type enum."""
    INPUT = 1
    HIDDEN = 2
    OUTPUT = 3