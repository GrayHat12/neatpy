from typing import Optional
from config import PROBABILITY_INDIVIDUAL_WEIGHT_REASSIGNMENT, WEIGHT_RANDOM_STRENGTH, WEIGHT_SHIFT_STRENGTH
from src.gene import Gene
from src.node_gene import NodeGene
import random


class ConnectionGene(Gene):
    from_node: NodeGene
    to_node: NodeGene
    __enabled: bool
    _INNOVATION_NUMBER: int

    def __init__(self, from_node: NodeGene, to_node: NodeGene, innovation_number: int, weight: Optional[float] = None, enabled: bool = True) -> None:
        super().__init__()
        self.from_node = from_node
        self.to_node = to_node
        self._INNOVATION_NUMBER = innovation_number
        if not isinstance(weight, float):
            weight = random.random()
        self._weight = weight
        if not isinstance(enabled, bool):
            enabled = False
        self.__enabled = enabled
    
    @property
    def enabled(self):
        return self.__enabled

    def mutate_enabled(self):
        self.__enabled = not self.__enabled

    def mutate_weight(self):
        event = random.random()
        if PROBABILITY_INDIVIDUAL_WEIGHT_REASSIGNMENT > event:
            self._weight = (random.random() * 2 - 1) * WEIGHT_RANDOM_STRENGTH
        else:
            self._weight += (random.random() * 2 - 1) * WEIGHT_SHIFT_STRENGTH

    def copy(self) -> 'ConnectionGene':
        return ConnectionGene(
            from_node=self.from_node,
            to_node=self.to_node,
            innovation_number=self._INNOVATION_NUMBER,
            weight=self._weight,
            enabled=self.__enabled
        )
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, ConnectionGene):
            return self.innovation_number == __o.innovation_number
        return False
    
    def __hash__(self) -> int:
        return self.innovation_number
    
    def __str__(self) -> str:
        return f"{self.innovation_number}:{str(self.from_node)}{'=>' if self.enabled else '->'}{str(self.to_node)}"