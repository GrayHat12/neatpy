import random
from typing import List, Optional, Tuple, Dict, Generator
from config import DISTANCE_AVG_WEIGHT_DIFF_IMPORTANCE, DISTANCE_DISJOINT_GENES_IMPORTANCE, DISTANCE_EXCESS_GENES_IMPORTANCE, PROBABILITY_CONNECTION_MUTATION, PROBABILITY_CROSSOVER_CONNECTION_DISABLED, PROBABILITY_NODE_MUTATION, PROBABILITY_WEIGHT_MUTATION

from src.connection_gene import ConnectionGene
# from src.gene_store import get_connection_innovation_number, get_node_innovation_number, update_connection_gene_store, update_node_gene_store, get_next_node_innovation_number
# from src.state import State
from utils.enums import NodeType
from src.node_gene import NodeGene
from src.graph_mapper import populate_nodes


class Genome:
    __node_genes: Dict[int, NodeGene]
    __connection_genes: Dict[str, ConnectionGene]

    def __init__(self) -> None:
        self.__node_genes = {}
        self.__connection_genes = {}
        # self.__state = State()
    
    @property
    def hidden_node_count(self):
        return len([node for node in self.node_genes if node.node_type == NodeType.HIDDEN])
    
    def remove_useless_leafs(self):
        useless_nodes: List[int] = []
        output_nodes:List[NodeGene] = []
        _all_nodes:List[NodeGene] = self.node_genes
        _all_connections:List[ConnectionGene] = self.connection_genes
        for node in _all_nodes:
            if node.node_type in [NodeType.OUTPUT, NodeType.INPUT]:
                if node.node_type == NodeType.OUTPUT:
                    output_nodes.append(node)
                continue
            useless_nodes.append(node.innovation_number)
        def connections_to_node(node: int, all_connections: List[ConnectionGene]):
            for connection in all_connections:
                if connection.to_node == node:
                    yield connection
        def recursive_browse_connections(connections: Generator[ConnectionGene, None, None], all_connections: List[ConnectionGene]):
            for connection in connections:
                if connection.from_node in useless_nodes:
                    useless_nodes.remove(connection.from_node)
                if connection.to_node in useless_nodes:
                    useless_nodes.remove(connection.to_node)
                recursive_browse_connections(connections_to_node(connection.from_node, all_connections), all_connections)
                # recursive_browse_connections(connections_to_node(connection.to_node, all_connections), all_connections)
        for output_node in output_nodes:
            recursive_browse_connections(connections_to_node(output_node.innovation_number, _all_connections), _all_connections)
        for node in useless_nodes:
            self.__node_genes.pop(node)
            for connection in self.connection_genes:
                if connection.from_node == node or connection.to_node == node:
                    if connection.innovation_number in self.__connection_genes:
                        self.__connection_genes.pop(connection.innovation_number)

    @property
    def _next_node_innovation(self):
        return max(list(self.__node_genes.keys()) + [0]) + 1

    def get_node(self, innovation_number: int):
        return self.__node_genes.get(innovation_number, None)
    
    def add_node(self, node: NodeGene):
        self.__node_genes.update({node.innovation_number: node})
    
    def get_connection(self, innovation_number: int):
        return self.__connection_genes.get(innovation_number, None)

    def calculate_result(self, *args: float):
        input_nodes: List[NodeGene] = [
            node for node in self.node_genes if node.node_type == NodeType.INPUT]
        if len(input_nodes) != len(args):
            print(len(input_nodes), len(args),
                  self.__node_genes, self.__connection_genes)
            print(input_nodes)
            raise ValueError(
                "Number of input nodes does not match number of arguments")
        # gene_graph_mapper = GeneGraphMapper(self.node_genes, self.connection_genes)
        try:
            return populate_nodes(self.connection_genes, self.node_genes, *args)
        except Exception as e:
            print(self)
            raise e
        # return gene_graph_mapper.propagate(*args)

    def connection_mutation(self, nodes: Optional[Tuple[NodeGene, NodeGene]] = None):
        """
        Add a connection between 2 nodes
        """
        node_from, node_to = None, None

        if isinstance(nodes, tuple):
            if len(nodes) == 2:
                if isinstance(nodes[0], NodeGene) and isinstance(nodes[1], NodeGene):
                    node_from, node_to = nodes

        if None in [node_from, node_to]:
            node_from = random.choice(self.node_genes)
            remaining = [node for node in self.node_genes if node != node_from and node.x_axis > node_from.x_axis]
            if not remaining:
                # Does not have any remaining valid nodes
                return
            node_to = random.choice(remaining)

        if node_from.innovation_number not in self.__node_genes or node_to.innovation_number not in self.__node_genes:
            raise ValueError(
                "Connection Mutation Failed, One or more nodes are not in the genome")

        # If both nodes are on the same x_axis, do not create connection
        if node_from.x_axis == node_to.x_axis:
            # print("Connection Mutation Failed, Both nodes on same axis")
            return

        # if NodeType.INPUT in [node_from.node_type, node_to.node_type] or NodeType.OUTPUT in [node_from.node_type, node_to.node_type]:
        #     # Correctly set the from_node and to_node
        #     if node_from.x_axis > node_to.x_axis:
        #         node_from, node_to = node_to, node_from
        if node_from.x_axis > node_to.x_axis:
            node_from, node_to = node_to, node_from

        # Check if connection already exists
        for connection in self.connection_genes:
            if connection.from_node == node_from.innovation_number and connection.to_node == node_to.innovation_number:
                # print("Connection Mutation Failed, Connection already exists")
                return

        # Create connection
        self.create_connection(node_from.innovation_number,
                               node_to.innovation_number)
        # print("Connection Mutation Successful")

    def node_mutation(self, connection_to_break: Optional[ConnectionGene] = None):
        """
        Break a connection into two, adding a node in between
        """
        if not isinstance(connection_to_break, ConnectionGene):
            connection_to_break = random.choice(self.connection_genes)

        if connection_to_break.innovation_number not in self.__connection_genes:
            raise ValueError(
                "Node Mutation Failed, Connection is not in the genome")

        # Break connection only if it is not disabled
        # if not connection_to_break.enabled:
        #     print("Node Mutation Failed, Connection is disabled")
        #     return

        # Create new node
        node_a = self.__node_genes[connection_to_break.from_node]
        node_b = self.__node_genes[connection_to_break.to_node]
        if not (node_a.innovation_number in self.__node_genes and node_b.innovation_number in self.__node_genes):
            raise ValueError(
                "Node Mutation Failed, One or more nodes are not in the genome")
        middle_x = (node_a.x_axis + node_b.x_axis) / 2
        # print('Selected Nodes', (node_a.innovation_number, node_a.x_axis), (node_b.innovation_number, node_b.x_axis))
        # print('Middle X', middle_x)
        new_node = NodeGene(
            self._next_node_innovation,
            node_type=NodeType.HIDDEN,
            x_axis=middle_x,
        )
        # print('New Node', new_node.innovation_number, new_node.x_axis)
        self.add_node(new_node)
        
        # Disable existing connection
        if connection_to_break.enabled:
            connection_to_break.mutate_enabled()

        # Create new connection
        self.create_connection(node_a.innovation_number,
                               new_node.innovation_number, weight=1)
        self.create_connection(
            new_node.innovation_number, node_b.innovation_number, weight=connection_to_break.weight)

        # print("Node Mutation Successful")

    def weight_mutation(self):
        random_connection = random.choice(self.connection_genes)
        # inn = random_connection.innovation_number
        # print("Weight before", random_connection.weight)
        # print("Weight Mutation", random_connection)
        random_connection.mutate_weight()
        # print("Weight after", self.__state.get_connection(inn).weight)
        # for connection in self.connection_genes:
        #     connection.mutate_weight()
        # print("Weight Mutation Successful")

    def create_connection(self, from_node: int, to_node: int, weight: Optional[float] = None, enabled: bool = True):
        # if from_node == 5 and to_node == 4:
        #     print('5,4 issue')
        #     for node in self.node_genes:
        #         print(node.innovation_number, node.x_axis)
        #     for conn in self.connection_genes:
        #         print(conn)
        if self.__node_genes[from_node].x_axis >= self.__node_genes[to_node].x_axis:
            raise ValueError(
                "Cannot create connection, from_node must be on the left of to_node")
        if from_node in self.__node_genes and to_node in self.__node_genes:
            connection = self.__connection_genes.get(
                f"{from_node}->{to_node}", None)
            if not connection:
                connection = ConnectionGene(
                    from_node=from_node,
                    to_node=to_node,
                )
            if weight:
                connection.set_weight(weight)
            if isinstance(enabled, bool):
                connection.set_enabled(enabled)
            self.__connection_genes.update(
                {connection.innovation_number: connection})
        else:
            raise ValueError("One or more nodes are not in the genome")

    # def generate_initial_nodes(self, input_nodes: int, output_nodes: int, weight_range: Tuple[float, float]):
    #     inp_nodes: List[int] = []
    #     for _ in range(input_nodes):
    #         node = self.__state.create_node(NodeType.INPUT, random.uniform(*weight_range))
    #         inp_nodes.append(node.innovation_number)
    #         self.add_node(node.innovation_number)

    #     for _ in range(output_nodes):
    #         node = self.__state.create_node(NodeType.OUTPUT, random.uniform(*weight_range))
    #         self.add_node(node.innovation_number)
    #         for inp_node in inp_nodes:
    #             self.create_connection(inp_node, node.innovation_number)

    def mutate(self):
        event = random.random()
        sorted_actions = sorted([
            (PROBABILITY_NODE_MUTATION, self.node_mutation),
            (PROBABILITY_CONNECTION_MUTATION, self.connection_mutation),
            (PROBABILITY_WEIGHT_MUTATION, self.weight_mutation),
        ], key=lambda x: x[0])
        for event_threshold, action in sorted_actions:
            if event < event_threshold:
                action()
                break
            # event -= event_threshold
        # if PROBABILITY_NODE_MUTATION > random.random():
        #     self.node_mutation()
        # elif PROBABILITY_CONNECTION_MUTATION > random.random():
        #     self.connection_mutation()
        # elif PROBABILITY_WEIGHT_MUTATION > random.random():
        #     self.weight_mutation()

    @property
    def node_genes(self):
        return list(self.__node_genes.values()).copy()

    @property
    def connection_genes(self):
        return list(self.__connection_genes.values()).copy()

    @staticmethod
    def distance(genome_a: 'Genome', genome_b: 'Genome') -> float:
        """
        Calculate 'E' excess genes
        Calculate 'D' disjoint genes
        Calculate 'W' Average weight difference between matching genes
        'N' is number of genes in larger one
        @returns C1*E/N + C2*D/N + C3*W
        """
        max_innovation_number = max(
            max([connection.innovation_number for connection in genome_a.connection_genes]),
            max([connection.innovation_number for connection in genome_b.connection_genes])
        )
        min_innovation_number = min(
            min([connection.innovation_number for connection in genome_a.connection_genes]),
            min([connection.innovation_number for connection in genome_b.connection_genes])
        )

        connections_larger: List[ConnectionGene] = []
        connections_smaller: List[ConnectionGene] = []
        for innovation in range(min_innovation_number, max_innovation_number+1):
            inn_a = None
            inn_b = None
            for connection in genome_a.connection_genes:
                if connection.innovation_number == innovation:
                    inn_a = connection
                    break
            for connection in genome_b.connection_genes:
                if connection.innovation_number == innovation:
                    inn_b = connection
                    break
            connections_larger.append(inn_a)
            connections_smaller.append(inn_b)

        number_of_genes_in_larger_genome = len([
            connection for connection in connections_larger if connection is not None
        ])
        number_of_genes_in_smaller_genome = len([
            connection for connection in connections_smaller if connection is not None
        ])

        if number_of_genes_in_larger_genome < number_of_genes_in_smaller_genome:
            connections_larger, connections_smaller = connections_smaller, connections_larger

        max_innovation_number_for_smaller_genome = max([
            connection.innovation_number for connection in connections_smaller if connection is not None
        ])

        excess_genes = 0
        disjoint_genes = 0
        average_weight_difference = 0
        equal_genes = 0
        is_disjoint = number_of_genes_in_smaller_genome > 0

        for connection_large, connection_small in zip(connections_larger, connections_smaller):
            if isinstance(connection_small, ConnectionGene) and isinstance(connection_large, ConnectionGene):  # matching genes
                average_weight_difference += abs(
                    connection_large.weight - connection_small.weight)
                equal_genes += 1
            elif is_disjoint:  # disjoint genes
                disjoint_genes += 1
            else:  # excess genes
                excess_genes += 1
            if isinstance(connection_small, ConnectionGene):
                is_disjoint = connection_small.innovation_number < max_innovation_number_for_smaller_genome

        average_weight_difference /= equal_genes

        # print("Excess genes:", excess_genes)
        # print("Disjoint genes:", disjoint_genes)
        # print("Average weight difference:", average_weight_difference)
        # print("Number of genes in larger genome:",
        #       number_of_genes_in_larger_genome)

        return (DISTANCE_EXCESS_GENES_IMPORTANCE*excess_genes / number_of_genes_in_larger_genome) + \
            (DISTANCE_DISJOINT_GENES_IMPORTANCE*disjoint_genes / number_of_genes_in_larger_genome) + \
            (DISTANCE_AVG_WEIGHT_DIFF_IMPORTANCE * average_weight_difference)

    @staticmethod
    def crossover(genome_a: 'Genome', genome_b: 'Genome', equal_fitness: bool = False) -> 'Genome':
        """
        Crossover two genomes
        @param genome_a: More Fit genome
        @param genome_b: Less Fit genome
        """
        child_genome = Genome()

        # Input/Output nodes from fitter parent
        for node in genome_a.node_genes:
            if node.node_type in [NodeType.INPUT, NodeType.OUTPUT]:
                _node = NodeGene(
                    child_genome._next_node_innovation,
                    weight=node.weight,
                    node_type=node.node_type,
                )
                child_genome.add_node(_node)

        # copied_nodes = {}

        # Node genes from the fitter parent
        # for node_gene in genome_a.node_genes:
        #     node = state.copy_node(node_gene.innovation_number)
        #     child_genome.add_node(node.innovation_number)
        #     copied_nodes[node_gene.innovation_number] = node.innovation_number

        # if equal_fitness:
        #     # Node genes from the other equally fit parent
        #     for node_gene in genome_b.node_genes:
        #         if node_gene not in genome_a.node_genes:
        #             node = state.copy_node(node_gene.innovation_number)
        #             child_genome.add_node(node.innovation_number)
        #             copied_nodes[node_gene.innovation_number] = node.innovation_number

        for connection_gene in genome_a.connection_genes:
            child_gene = None
            selected_parent = None
            if connection_gene in genome_b.connection_genes:  # matching gene, choose randomly
                from_parent_a = (connection_gene, genome_a)
                from_parent_b = (genome_b.connection_genes[genome_b.connection_genes.index(
                    connection_gene)], genome_b)
                is_disabled = False in [
                    from_parent_a[0].enabled, from_parent_b[0].enabled]
                child_gene, selected_parent = random.choice(
                    [from_parent_a, from_parent_b])
                child_gene = child_gene.copy()
                # child_gene.from_node = copied_nodes[child_gene.from_node]
                # child_gene.to_node = copied_nodes[child_gene.to_node]
                if is_disabled and PROBABILITY_CROSSOVER_CONNECTION_DISABLED > random.random():
                    if child_gene.enabled:
                        # if parent has disabled gene and we fall in probability, set child disabled
                        child_gene.mutate_enabled()
                else:
                    if not child_gene.enabled:
                        # if we do not fall in probability and child has disabled gene, set child enabled
                        child_gene.mutate_enabled()
            else:  # Excess or disjoint gene, take all from fitter parent
                # state.copy_connection(connection_gene.innovation_number)
                child_gene = connection_gene.copy()
                selected_parent = genome_a
                # child_gene.from_node = copied_nodes[connection_gene.from_node]
                # child_gene.to_node = copied_nodes[connection_gene.to_node]
            if isinstance(child_gene, ConnectionGene) and child_gene not in child_genome.connection_genes:
                _from_node = selected_parent.get_node(child_gene.from_node)
                _to_node = selected_parent.get_node(child_gene.to_node)
                from_node = NodeGene(
                    child_genome._next_node_innovation,
                    weight=_from_node.weight,
                    node_type=_from_node.node_type,
                    x_axis=_from_node.x_axis,
                )
                if from_node.node_type == NodeType.INPUT:
                    from_node = child_genome.get_node(_from_node.innovation_number)
                child_genome.add_node(from_node)
                to_node = NodeGene(
                    child_genome._next_node_innovation,
                    weight=_to_node.weight,
                    node_type=_to_node.node_type,
                    x_axis=_to_node.x_axis,
                )
                if to_node.node_type == NodeType.OUTPUT:
                    to_node = child_genome.get_node(_to_node.innovation_number)
                child_genome.add_node(to_node)
                try:
                    child_genome.create_connection(
                        from_node.innovation_number,
                        to_node.innovation_number,
                        weight=child_gene.weight,
                        enabled=child_gene.enabled
                    )
                except Exception as e:
                    print(child_genome)
                    raise e

        # if equal_fitness:
        #     # Add the rest of the genes from the other parent
        #     for connection_gene in genome_b.connection_genes:
        #         if genome_b.get_node(connection_gene.from_node).node_type == NodeType.INPUT or genome_b.get_node(connection_gene.to_node).node_type == NodeType.OUTPUT:
        #             continue
        #         if connection_gene not in child_genome.connection_genes:
        #             from_node = NodeGene(
        #                 child_genome._next_node_innovation,
        #                 weight=genome_b.get_node(connection_gene.from_node).weight,
        #                 node_type=genome_b.get_node(connection_gene.from_node).node_type,
        #                 x_axis=genome_b.get_node(connection_gene.from_node).x_axis
        #             )
        #             if from_node.node_type == NodeType.INPUT:
        #                 from_node = child_genome.get_node(connection_gene.from_node)
        #             child_genome.add_node(from_node)
        #             to_node = NodeGene(
        #                 child_genome._next_node_innovation,
        #                 weight=genome_b.get_node(connection_gene.to_node).weight,
        #                 node_type=genome_b.get_node(connection_gene.to_node).node_type,
        #                 x_axis=genome_b.get_node(connection_gene.to_node).x_axis
        #             )
        #             if to_node.node_type == NodeType.OUTPUT:
        #                 to_node = child_genome.get_node(connection_gene.to_node)
        #             child_genome.add_node(to_node)
        #             # conn.from_node = copied_nodes[connection_gene.from_node]
        #             # conn.to_node = copied_nodes[connection_gene.to_node]
        #             child_genome.create_connection(
        #                 from_node,
        #                 to_node,
        #                 weight=connection_gene.weight,
        #                 enabled=connection_gene.enabled
        #             )

        return child_genome

    def __str__(self) -> str:
        out = ""
        for connection in self.connection_genes:
            message = str(connection)
            if out != "":
                out += " "
            out += f'{message:{" "}{"<"}{8}}'
            out += "|"
        return out

    def copy(self):
        genome = Genome()
        for node_gene in self.node_genes:
            genome.add_node(node_gene.copy())
        for connection_gene in self.connection_genes:
            try:
                genome.create_connection(
                    connection_gene.from_node,
                    connection_gene.to_node,
                    weight=connection_gene.weight,
                    enabled=connection_gene.enabled
                )
            except Exception as e:
                for node in self.node_genes:
                    print(node, node.x_axis)
                print(self)
                raise e
        return genome
