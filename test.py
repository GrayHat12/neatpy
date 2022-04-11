from src.connection_gene import ConnectionGene
from utils.enums import NodeType
from utils.visualize import plot_genome
from src.genome import Genome
from src.node_gene import NodeGene


def get_parent1():
    parent1 = Genome()
    parent1.add_node_gene(
        NodeGene(parent1.next_node_innovation, node_type=NodeType.INPUT)
    )
    parent1.add_node_gene(
        NodeGene(parent1.next_node_innovation, node_type=NodeType.INPUT)
    )
    parent1.add_node_gene(
        NodeGene(parent1.next_node_innovation, node_type=NodeType.INPUT)
    )
    parent1.add_node_gene(
        NodeGene(parent1.next_node_innovation, node_type=NodeType.OUTPUT)
    )

    parent1.add_connection_gene(
        ConnectionGene(
            NodeGene(1, node_type=NodeType.INPUT),
            NodeGene(4, node_type=NodeType.OUTPUT),
            parent1.next_connection_innovation
        )
    )
    parent1.add_connection_gene(
        ConnectionGene(
            NodeGene(2, node_type=NodeType.INPUT),
            NodeGene(4, node_type=NodeType.OUTPUT),
            parent1.next_connection_innovation
        )
    )
    parent1.add_connection_gene(
        ConnectionGene(
            NodeGene(3, node_type=NodeType.INPUT),
            NodeGene(4, node_type=NodeType.OUTPUT),
            parent1.next_connection_innovation
        )
    )

    parent1.mutate_node(parent1.connection_genes[1])

    parent1.mutate_connection(
        parent1.node_genes[-1],
        NodeGene(1, node_type=NodeType.INPUT)
    )
    return parent1


def get_parent2():
    parent = Genome()
    parent.add_node_gene(
        NodeGene(parent.next_node_innovation, node_type=NodeType.INPUT)
    )
    parent.add_node_gene(
        NodeGene(parent.next_node_innovation, node_type=NodeType.INPUT)
    )
    parent.add_node_gene(
        NodeGene(parent.next_node_innovation, node_type=NodeType.INPUT)
    )
    parent.add_node_gene(
        NodeGene(parent.next_node_innovation, node_type=NodeType.OUTPUT)
    )

    parent.add_connection_gene(
        ConnectionGene(
            NodeGene(1, node_type=NodeType.INPUT),
            NodeGene(4, node_type=NodeType.OUTPUT),
            parent.next_connection_innovation
        )
    )
    parent.add_connection_gene(
        ConnectionGene(
            NodeGene(2, node_type=NodeType.INPUT),
            NodeGene(4, node_type=NodeType.OUTPUT),
            parent.next_connection_innovation
        )
    )
    parent.add_connection_gene(
        ConnectionGene(
            NodeGene(3, node_type=NodeType.INPUT),
            NodeGene(4, node_type=NodeType.OUTPUT),
            parent.next_connection_innovation
        )
    )

    print([str(node) for node in parent.connection_genes])

    parent.mutate_node(parent.connection_genes[1])
    parent.mutate_node(parent.connection_genes[4])

    parent.mutate_connection(
        parent.node_genes[2],
        parent.node_genes[4]
    )
    parent.mutate_connection(
        parent.node_genes[0],
        parent.node_genes[-1]
    )

    return parent


def test_crossover():
    parent1 = get_parent1()
    parent2 = get_parent2()

    plot_genome(parent1, filename='./plots/parent 1', show_disabled=False)
    plot_genome(parent2, filename='./plots/parent 2', show_disabled=False)

    child = Genome.crossover(parent2, parent1, True)

    plot_genome(child, filename='./plots/child', show_disabled=False)


def test_node_mutation():
    genome = get_parent1()
    plot_genome(genome, filename='./plots/before_node_mutation',
                show_disabled=False)
    genome.node_mutation()
    plot_genome(genome, filename='./plots/after_node_mutation',
                show_disabled=False)

def test_connection_mutation():
    genome = get_parent2()
    plot_genome(genome, filename='./plots/before_connection_mutation',
                show_disabled=False)
    genome.connection_mutation()
    plot_genome(genome, filename='./plots/after_connection_mutation',
                show_disabled=False)


if __name__ == '__main__':
    test_node_mutation()
    test_connection_mutation()