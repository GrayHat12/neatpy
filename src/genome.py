import random
from typing import List, Optional, Tuple
from config import DISTANCE_AVG_WEIGHT_DIFF_IMPORTANCE, DISTANCE_DISJOINT_GENES_IMPORTANCE, DISTANCE_EXCESS_GENES_IMPORTANCE, PROBABILITY_CONNECTION_MUTATION, PROBABILITY_CROSSOVER_CONNECTION_DISABLED, PROBABILITY_NODE_MUTATION, PROBABILITY_WEIGHT_MUTATION

from src.connection_gene import ConnectionGene
from src.gene_store import get_connection_innovation_number, get_node_innovation_number, update_connection_gene_store, update_node_gene_store
from utils.enums import NodeType
from src.node_gene import NodeGene


class Genome:
    __node_genes: List[NodeGene]
    __connection_genes: List[ConnectionGene]

    def __init__(self) -> None:
        self.__node_genes = []
        self.__connection_genes = []

    def add_node_gene(self, node_gene: NodeGene):
        update_node_gene_store(node_gene.innovation_number)
        self.__node_genes.append(node_gene)

    def add_connection_gene(self, connection_gene: ConnectionGene):
        update_connection_gene_store(connection_gene.from_node.innovation_number,
                                     connection_gene.to_node.innovation_number, connection_gene.innovation_number)
        self.__connection_genes.append(connection_gene)

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
            node_from = random.choice(self.__node_genes)
            node_to = random.choice(self.__node_genes)

        if node_from not in self.__node_genes or node_to not in self.__node_genes:
            raise ValueError(
                "Connection Mutation Failed, One or more nodes are not in the genome")

        # If both nodes are on the same x_axis, do not create connection
        if node_from.x_axis == node_to.x_axis:
            print("Connection Mutation Failed, Both nodes on same axis")
            return

        if NodeType.INPUT in [node_from.node_type, node_to.node_type] or NodeType.OUTPUT in [node_from.node_type, node_to.node_type]:
            # Correctly set the from_node and to_node
            if node_from.x_axis > node_to.x_axis:
                node_from, node_to = node_to, node_from

        # Check if connection already exists
        for connection in self.__connection_genes:
            if connection.from_node == node_from and connection.to_node == node_to:
                print("Connection Mutation Failed, Connection already exists")
                return

        # Create connection
        self.create_connection(node_from, node_to)
        print("Connection Mutation Successful")

    def node_mutation(self, connection_to_break: Optional[ConnectionGene] = None):
        """
        Break a connection into two, adding a node in between
        """
        if not isinstance(connection_to_break, ConnectionGene):
            connection_to_break = random.choice(self.__connection_genes)

        if connection_to_break not in self.__connection_genes:
            raise ValueError(
                "Node Mutation Failed, Connection is not in the genome")

        # Break connection only if it is not disabled
        # if not connection_to_break.enabled:
        #     print("Node Mutation Failed, Connection is disabled")
        #     return

        # Create new node
        node_a = connection_to_break.from_node
        node_b = connection_to_break.to_node
        middle_x = (node_a.x_axis + node_b.x_axis) / 2
        new_node = self.create_node(middle_x, get_node_innovation_number(
            node_a.innovation_number, node_b.innovation_number))

        # Disable existing connection
        if connection_to_break.enabled:
            connection_to_break.mutate_enabled()

        # Create new connection
        self.create_connection(node_a, new_node, weight=1)
        self.create_connection(
            new_node, node_b, weight=connection_to_break.weight)

        print("Node Mutation Successful")

    def weight_mutation(self):
        for connection in self.connection_genes:
            connection.mutate_weight()
        print("Weight Mutation Successful")

    def create_connection(self, from_node: NodeGene, to_node: NodeGene, weight: Optional[float] = None, enabled: bool = True):
        innovation = get_connection_innovation_number(
            from_node.innovation_number, to_node.innovation_number)
        if from_node in self.__node_genes and to_node in self.__node_genes:
            self.__connection_genes.append(
                ConnectionGene(
                    from_node, to_node, innovation, weight=weight, enabled=enabled)
            )
        else:
            raise ValueError("One or more nodes are not in the genome")

    def create_node(self, x_axis: float, innovation_number: int):
        new_node = NodeGene(x_axis=x_axis, innovation_number=innovation_number)
        self.__node_genes.append(new_node)
        return new_node

    def mutate(self):
        if PROBABILITY_NODE_MUTATION > random.random():
            self.node_mutation()
        if PROBABILITY_CONNECTION_MUTATION > random.random():
            self.connection_mutation()
        if PROBABILITY_WEIGHT_MUTATION > random.random():
            self.weight_mutation()

    @property
    def node_genes(self):
        return self.__node_genes

    @property
    def connection_genes(self):
        return self.__connection_genes

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

        connections_larger = []
        connections_smaller = []
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

        print("Excess genes:", excess_genes)
        print("Disjoint genes:", disjoint_genes)
        print("Average weight difference:", average_weight_difference)
        print("Number of genes in larger genome:",
              number_of_genes_in_larger_genome)

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

        # Node genes from the fitter parent
        for node_gene in genome_a.node_genes:
            child_genome.add_node_gene(node_gene.copy())

        if equal_fitness:
            # Node genes from the other equally fit parent
            for node_gene in genome_b.node_genes:
                if node_gene not in genome_a.node_genes:
                    child_genome.add_node_gene(node_gene.copy())

        for connection_gene in genome_a.connection_genes:
            child_gene = None
            if connection_gene in genome_b.connection_genes:  # matching gene, choose randomly
                from_parent_a = connection_gene
                from_parent_b = genome_b.connection_genes[genome_b.connection_genes.index(
                    connection_gene)]
                is_disabled = False in [
                    from_parent_a.enabled, from_parent_b.enabled]
                child_gene = random.choice(
                    [from_parent_a, from_parent_b]).copy()
                if is_disabled and PROBABILITY_CROSSOVER_CONNECTION_DISABLED > random.random():
                    if child_gene.enabled:
                        # if parent has disabled gene and we fall in probability, set child disabled
                        child_gene.mutate_enabled()
                else:
                    if not child_gene.enabled:
                        # if we do not fall in probability and child has disabled gene, set child enabled
                        child_gene.mutate_enabled()
            else:  # Excess or disjoint gene, take all from fitter parent
                child_gene = connection_gene.copy()
            if isinstance(child_gene, ConnectionGene) and child_gene not in child_genome.connection_genes:
                child_genome.add_connection_gene(child_gene)

        if equal_fitness:
            # Add the rest of the genes from the other parent
            for connection_gene in genome_b.connection_genes:
                if connection_gene not in child_genome.connection_genes:
                    child_genome.add_connection_gene(connection_gene.copy())

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
