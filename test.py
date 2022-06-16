from src.genome_config import GenomeConfig
from utils.visualize import plot_genome
from src.genome import Genome

def test_crossover():
    parent1 = GenomeConfig("./test_architectures/parent1.save").load()
    print('Parent 1',parent1)
    parent2 = GenomeConfig("./test_architectures/parent2.save").load()

    plot_genome(parent1, filename='./plots/parent 1', show_disabled=False)
    plot_genome(parent2, filename='./plots/parent 2', show_disabled=False)

    child = Genome.crossover(parent2, parent1, True)

    plot_genome(child, filename='./plots/child', show_disabled=False)
    GenomeConfig("./test_architectures/child.save").save(child)


def test_node_mutation():
    genome = GenomeConfig("./test_architectures/parent1.save").load()
    plot_genome(genome, filename='./plots/before_node_mutation',
                show_disabled=False)
    genome.node_mutation()
    plot_genome(genome, filename='./plots/after_node_mutation',
                show_disabled=False)

def test_connection_mutation():
    genome = GenomeConfig("./test_architectures/parent2.save").load()
    plot_genome(genome, filename='./plots/before_connection_mutation',
                show_disabled=False)
    genome.connection_mutation()
    plot_genome(genome, filename='./plots/after_connection_mutation',
                show_disabled=False)

def test_distance_function():
    genome1 = GenomeConfig("./test_architectures/parent1.save").load()
    genome2 = GenomeConfig("./test_architectures/parent2.save").load()

    genome_distance = Genome.distance(genome1, genome2)

    same_genome_distance = Genome.distance(genome1, genome1)

    print("Genome Distance :", genome_distance)
    print("Same Genome Distance :", same_genome_distance)

if __name__ == '__main__':
    test_crossover()
    test_node_mutation()
    test_connection_mutation()
    test_distance_function()