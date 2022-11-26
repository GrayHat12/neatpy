from typing import List, Dict, Optional
from src.node_gene import NodeGene
from src.connection_gene import ConnectionGene
from utils.enums import NodeType


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class State():
    def __init__(self):
        self._nodes: Dict[int, NodeGene] = {}
        self._connections: Dict[int, ConnectionGene] = {}

    def copy(self):
        new_state = State()
        for node in self.nodes:
            new_state._nodes[node.innovation_number] = node.copy()
        for connection in self.connections:
            new_state._connections[connection.innovation_number] = connection.copy()
        return new_state

    @property
    def nodes(self):
        return list(self._nodes.values())

    @property
    def connections(self):
        return list(self._connections.values())
    
    @property
    def _next_node_innovation(self):
        return max(list(self._nodes.keys()) + [0]) + 1
    
    @property
    def _next_connection_innovation(self):
        return max(list(self._connections.keys()) + [0]) + 1

    def create_node(self, node_type: NodeType = NodeType.HIDDEN, weight: Optional[float] = None, x_axis: Optional[float] = None) -> NodeGene:
        node = NodeGene(self._next_node_innovation, weight=weight, node_type=node_type, x_axis=x_axis)
        self._nodes[node.innovation_number] = node
        return node
    
    def get_connection_by_spec(self, from_inn: int, to_inn: int):
        for connection in self.connections:
            if connection.from_node == from_inn and connection.to_node == to_inn:
                return connection
        node_from = self._nodes[from_inn]
        node_to = self._nodes[to_inn]
        if not node_from or not node_to:
            raise Exception("Invalid node")
        connection = ConnectionGene(from_inn, to_inn, self._next_connection_innovation)
        self._connections[connection.innovation_number] = connection
        return connection
    
    def get_node(self, node_inn: int):
        return self._nodes[node_inn]
    
    def get_connection(self, innovation: int):
        return self._connections[innovation]
    
    def copy_node(self, innovation: int):
        existing = self._nodes[innovation]
        if not isinstance(existing, NodeGene):
            raise Exception("Invalid node")
        node = NodeGene(self._next_node_innovation, weight=existing.weight, node_type=existing.node_type, x_axis=existing.x_axis)
        self._nodes[node.innovation_number] = node
        return node

    def copy_connection(self, innovation: int):
        existing = self._connections[innovation]
        if not isinstance(existing, ConnectionGene):
            raise Exception("Invalid connection")
        connection = ConnectionGene(existing.from_node, existing.to_node, self._next_connection_innovation, weight=existing.weight, enabled=existing.enabled)
        self._connections[connection.innovation_number] = connection
        return connection
    
    def get_connections_with_same_weight(self):
        connections = {}
        for connection in self.connections:
            if connection.weight not in connections:
                connections[connection.weight] = []
            connections[connection.weight].append(connection)
        return connections