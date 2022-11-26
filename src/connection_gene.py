from typing import Optional
from config import PROBABILITY_INDIVIDUAL_WEIGHT_REASSIGNMENT, WEIGHT_RANDOM_STRENGTH, WEIGHT_SHIFT_STRENGTH
from src.gene import Gene
import random


class ConnectionGene(Gene):
    from_node: int
    to_node: int
    __enabled: bool
    _INNOVATION_NUMBER: str

    def __init__(self, from_node: int, to_node: int, weight: Optional[float] = None, enabled: bool = True) -> None:
        super().__init__()
        self.from_node = from_node
        self.to_node = to_node
        # if not (isinstance(weight, float) or isinstance(weight, int)):
        #     weight = random.random()
        try:
            weight = float(weight)
        except TypeError:
            weight = random.random()
        self._weight = weight
        if not isinstance(enabled, bool):
            enabled = False
        self.__enabled = enabled
    
    @property
    def enabled(self):
        return self.__enabled
    
    @property
    def innovation_number(self):
        return f"{self.from_node}->{self.to_node}"

    def mutate_enabled(self):
        self.__enabled = not self.__enabled

    def mutate_weight(self):
        event = random.random()
        sign = random.choice([-1, 1])
        if PROBABILITY_INDIVIDUAL_WEIGHT_REASSIGNMENT > event:
            self._weight = (random.random() * sign) * WEIGHT_RANDOM_STRENGTH
        else:
            self._weight += (random.random() * sign) * WEIGHT_SHIFT_STRENGTH
        if self.weight < -1:
            self._weight = -1
        elif self.weight > 1:
            self._weight = 1

    def copy(self) -> 'ConnectionGene':
        return ConnectionGene(
            from_node=self.from_node,
            to_node=self.to_node,
            weight=self._weight,
            enabled=self.__enabled
        )
    
    def set_weight(self, weight: float):
        self._weight = weight
    
    def set_enabled(self, enabled: bool):
        self.__enabled = enabled
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, ConnectionGene):
            return self.innovation_number == __o.innovation_number
        return False
    
    def __hash__(self) -> int:
        return self.innovation_number
    
    def __str__(self) -> str:
        return f"{self.innovation_number}:{str(self.from_node)}{'=>' if self.enabled else '->'}{str(self.to_node)}"