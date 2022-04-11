import random
from typing import Optional
from utils.enums import NodeType
from src.gene import Gene


class NodeGene(Gene):

    __NODE_TYPE: NodeType
    __X_AXIS: float

    def __init__(self, innovation_number: int, weight: Optional[float] = None, node_type: Optional[NodeType] = NodeType.HIDDEN, x_axis: Optional[float] = None) -> None:
        self._INNOVATION_NUMBER = innovation_number
        if not isinstance(weight, float):
            weight = random.random()
        self._weight = weight
        if not isinstance(node_type, NodeType):
            node_type = NodeType.HIDDEN
        self.__NODE_TYPE = node_type
        if not isinstance(x_axis, float):
            if self.__NODE_TYPE == NodeType.INPUT:
                x_axis = 0.0
            elif self.__NODE_TYPE == NodeType.OUTPUT:
                x_axis = 1.0
            else:
                raise ValueError("Node type is not INPUT or OUTPUT, Please specify x_axis.")
        self.__X_AXIS = x_axis

    def copy(self) -> 'NodeGene':
        return NodeGene(
            innovation_number=self._INNOVATION_NUMBER,
            weight=self._weight,
            node_type=self.__NODE_TYPE,
            x_axis=self.__X_AXIS
        )

    @property
    def node_type(self):
        return self.__NODE_TYPE
    
    @property
    def x_axis(self):
        return self.__X_AXIS
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, NodeGene):
            return self.innovation_number == __o.innovation_number
        return False
    
    def __hash__(self) -> int:
        return self.innovation_number
    
    def __str__(self) -> str:
        return f"{self.innovation_number}"