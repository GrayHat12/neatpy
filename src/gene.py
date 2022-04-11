import random

class Gene:
    _INNOVATION_NUMBER: int
    _weight: float

    @property
    def innovation_number(self):
        return self._INNOVATION_NUMBER
    
    @property
    def weight(self):
        return self._weight
    
    def mutate_weight(self):
        self._weight += random.random() * 0.1 - 0.05 * random.choice([-1, 1])
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Gene):
            return self.innovation_number == __o.innovation_number
        return False
    
    def __hash__(self) -> int:
        return self.innovation_number