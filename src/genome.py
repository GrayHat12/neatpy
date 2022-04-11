import random
from typing import List, Optional, Tuple

from src.connection_gene import ConnectionGene
from utils.enums import NodeType
from src.node_gene import NodeGene


class Genome:
    __node_genes: List[NodeGene]
    __connection_genes: List[ConnectionGene]

    def __init__(self, number_of_inputs: int, number_of_outputs: int):
        self.__node_genes = [
            NodeGene(node_type=NodeType.INPUT if i < number_of_inputs else NodeType.OUTPUT) for i in range(number_of_inputs+number_of_outputs)
        ]
        self.__connection_genes = []

    def __init__(self) -> None:
        self.__node_genes = []
        self.__connection_genes = []

    def add_node_gene(self, node_gene: NodeGene):
        self.__node_genes.append(node_gene)

    def add_connection_gene(self, connection_gene: ConnectionGene):
        self.__connection_genes.append(connection_gene)

    def connection_mutation(self, nodes: Optional[Tuple[NodeGene, NodeGene]] = None):

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
        if not isinstance(connection_to_break, ConnectionGene):
            connection_to_break = random.choice(self.__connection_genes)

        if connection_to_break not in self.__connection_genes:
            raise ValueError(
                "Node Mutation Failed, Connection is not in the genome")

        # Break connection only if it is not disabled
        if not connection_to_break.enabled:
            print("Node Mutation Failed, Connection is disabled")
            return

        # Create new node
        node_a = connection_to_break.from_node
        node_b = connection_to_break.to_node
        middle_x = (node_a.x_axis + node_b.x_axis) / 2
        new_node = self.create_node(middle_x)

        # Disable existing connection
        connection_to_break.mutate_enabled()

        # Create new connection
        self.create_connection(node_a, new_node, weight=1)
        self.create_connection(
            new_node, node_b, weight=connection_to_break.weight)

        print("Node Mutation Successful")

    def mutate_node(self, connection: ConnectionGene):
        if connection not in self.__connection_genes:
            raise ValueError("Connection is not in the genome")
        return self.node_mutation(connection)

    def mutate_connection(self, from_node: NodeGene, to_node: NodeGene):
        if from_node in self.__node_genes and to_node in self.__node_genes:
            return self.connection_mutation((from_node, to_node))
        else:
            raise ValueError("One or more nodes are not in the genome")

    def create_connection(self, from_node: NodeGene, to_node: NodeGene, weight: Optional[float] = None, enabled: bool = True):
        if from_node in self.__node_genes and to_node in self.__node_genes:
            self.__connection_genes.append(
                ConnectionGene(
                    from_node, to_node, self.next_connection_innovation, weight=weight, enabled=enabled)
            )
        else:
            raise ValueError("One or more nodes are not in the genome")

    def create_node(self, x_axis: float, innovation_number: Optional[int] = None):
        if not isinstance(innovation_number, int):
            innovation_number = self.next_node_innovation
        new_node = NodeGene(x_axis=x_axis, innovation_number=innovation_number)
        self.__node_genes.append(new_node)
        return new_node

    @property
    def node_genes(self):
        return self.__node_genes

    @property
    def connection_genes(self):
        return self.__connection_genes

    @property
    def next_connection_innovation(self):
        return len(self.connection_genes) + 1

    @property
    def next_node_innovation(self):
        return len(self.node_genes) + 1

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
                child_gene = random.choice(
                    [from_parent_a, from_parent_b]).copy()
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
