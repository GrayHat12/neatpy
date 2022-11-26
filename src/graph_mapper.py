from typing import List, Dict, Set

from src.node_gene import NodeGene
from utils.enums import NodeType
from src.connection_gene import ConnectionGene


class GeneGraphConnection:
    def __init__(self, connection: ConnectionGene, from_node: 'GeneGraphNode', to_node: 'GeneGraphNode', graph: 'GeneGraphMapper') -> None:
        self.connection = connection
        self.from_node = from_node
        self.to_node = to_node
        self.graph = graph

    @property
    def output(self):
        return self.connection.weight * self.from_node.output


class GeneGraphNode:
    def __init__(self, node: NodeGene, graph: 'GeneGraphMapper') -> None:
        self.node = node
        self.graph = graph
        self.connections: List[GeneGraphConnection] = []
        self._input: List[float] = []

    @property
    def input(self):
        return self._input if self._input else [conn.output for conn in self.graph.connections_to_node(self.node)]

    @property
    def output(self):
        return self.node.weight * sum(self.input)

    def append_connection(self, connection: GeneGraphConnection):
        self.connections.append(connection)


class GeneGraphMapper:
    def __init__(self, nodes: List[NodeGene], connections: List[ConnectionGene]) -> None:
        self.nodes: Dict[int, GeneGraphNode] = {}
        for node in nodes:
            self.nodes[node.innovation_number] = GeneGraphNode(node, self)

        for connection in connections:
            if not connection.enabled:
                continue
            from_node = self.nodes[connection.from_node.innovation_number]
            to_node = self.nodes[connection.to_node.innovation_number]
            graph_connection = GeneGraphConnection(
                connection, from_node, to_node, self)
            from_node.append_connection(graph_connection)

    def connections_to_node(self, node: NodeGene):
        return [connection for connection in self.nodes[node.innovation_number].connections]

    def propagate(self, *inputs: float):
        input_nodes = [node for node in self.nodes.values(
        ) if node.node.node_type == NodeType.INPUT]
        output_nodes = [node for node in self.nodes.values(
        ) if node.node.node_type == NodeType.OUTPUT]
        if len(input_nodes) != len(inputs):
            raise ValueError(
                "Number of inputs does not match number of input nodes")

        for input, node in zip(inputs, input_nodes):
            node.input.append(input)

        output = []
        for node in output_nodes:
            output.append(node.output)

        return output


class Node:
    def __init__(self, node: NodeGene) -> None:
        self.node = node
        self.connections: List[Connection] = []
        self.output = 0
        self.calculated = False

    def calculate_output(self, inputs: List[float]):
        self.calculated = True
        self.output = self.node.weight * sum(inputs)


class Connection:
    def __init__(self, connection: ConnectionGene, from_node: Node, to_node: Node) -> None:
        self.connection = connection
        self.from_node: Node = from_node
        self.to_node: Node = to_node

    @property
    def output(self):
        return self.connection.weight * self.from_node.output


# def populate_nodes(connections: List[ConnectionGene], nodes: List[NodeGene], *inputs: float):
#     output_nodes: List[Node] = []
#     input_nodes: List[Node] = []
#     for node in nodes:
#         if node.node_type == NodeType.INPUT:
#             input_nodes.append(Node(node))
#         elif node.node_type == NodeType.OUTPUT:
#             output_nodes.append(Node(node))

#     for connection in connections:
#         to_node = Node(connection.to_node)
#         from_node = Node(connection.from_node)
#         to_node.connections.append(Connection(connection, from_node, to_node))
#         # if to_node not in output_nodes and to_node.node.node_type == NodeType.OUTPUT:
#         #     output_nodes.append(to_node)

#     if len(inputs) != len(input_nodes):
#         raise ValueError(
#             "Number of inputs does not match number of input nodes")

#     def propagate(nodes: List[Node], _inputs: List[float]):
#         connections: List[Connection] = []
#         for input, node in zip(_inputs, nodes):
#             node.calculate_output([input])
#             connections.extend(node.connections)
#         new_nodes: Dict[NodeGene, List[ConnectionGene]] = {}
#         for connection in connections:
#             if connection.from_node in nodes:
#                 if connection.to_node not in new_nodes:
#                     new_nodes[connection.to_node] = [connection]
#                 else:
#                     new_nodes[connection.to_node].append(connection)
#         if new_nodes:
#             _nodes: List[Node] = []
#             _new_inputs: List[float] = []
#             for node, connections in new_nodes.items():
#                 _nodes.append(node)
#                 _new_inputs.append(
#                     [connection.output for connection in connections])
#             propagate(_nodes, _new_inputs)

#     propagate(input_nodes, inputs)
#     print('Output Nodes', output_nodes, [node.output for node in output_nodes])
#     return [node.output for node in output_nodes]


def populate_nodes(connections: List[ConnectionGene], nodes: List[NodeGene], *inputs: float):
    input_nodes: Set[NodeGene] = set()
    output_nodes: Set[NodeGene] = set()
    hidden_nodes: Set[NodeGene] = set()
    for node in nodes:
        if node.node_type == NodeType.INPUT:
            input_nodes.add(node)
        elif node.node_type == NodeType.OUTPUT:
            output_nodes.add(node)
        elif node.node_type == NodeType.HIDDEN:
            hidden_nodes.add(node)
        else:
            raise ValueError("Unknown node type")
    if len(inputs) != len(input_nodes):
        raise ValueError(
            "Number of inputs does not match number of input nodes")
    level_nodes = {
        0: input_nodes,
        1: output_nodes
    }
    for hidden_node in hidden_nodes:
        if hidden_node.x_axis in level_nodes:
            level_nodes[hidden_node.x_axis].add(hidden_node)
        else:
            level_nodes[hidden_node.x_axis] = {hidden_node}
    levels = sorted(level_nodes.keys())

    node_config: Dict[NodeGene, Dict[str, List]] = {}

    for node, input in zip(input_nodes, inputs):
        node_config[node] = {
            'connections': [],
            'inputs': [input]
        }
    
    def find_connections(node_gene: NodeGene, connections_list: List[ConnectionGene]):
        for connection in connections_list:
            if connection.to_node == node_gene.innovation_number and connection.enabled:
                yield connection
    
    def find_node(node_genes: List[NodeGene], innovation: int):
        for node in node_genes:
            if node.innovation_number == innovation:
                return node
        print([node.innovation_number for node in node_genes], "not includes", innovation)
        raise ValueError("Invalid Innovation")
    
    for level in levels:
        if level == 0:
            continue
        for node in level_nodes[level]:
            node_config[node] = {
                'connections': [],
                'inputs': []
            }
            for connection in find_connections(node, connections):
                node_config[node]['connections'].append(connection)
                try:
                    output = sum(node_config[find_node(nodes, connection.from_node)]['inputs']) * connection.weight
                except Exception as e:
                    import json
                    _config = {}
                    for node in node_config:
                        _config[f"Node_{node.innovation_number}"] = node_config[node]
                    _level_nodes = {}
                    for _level in level_nodes:
                        _level_nodes[_level] = [node.innovation_number for node in level_nodes[_level]]
                    print(json.dumps(_level_nodes, indent=4, default=str))
                    print(connection, levels, level)
                    print(json.dumps(_config, indent=4, default=str))
                    raise e
                node_config[node]['inputs'].append(output)
    
    # with open('node_config.json', 'w+') as f:
    #     import json
    #     _config = {}
    #     for node in node_config:
    #         _config[f"Node_{node.innovation_number}"] = node_config[node]
    #     json.dump(_config, f, indent=4, default=str)
    
    output = []
    for node in output_nodes:
        output.append(sum(node_config[node]['inputs']))
    return output