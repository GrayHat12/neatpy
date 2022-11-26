from src.genome_config import GenomeConfig
from utils.visualize import plot_genome
from src.genome import Genome
from tests.xor import XorNeat
from tests.equation import EquationNeat
from src.neat import NeatConfig


def dec_to_bin(x):
    return [int(a) for a in bin(x)[2:]]

def test_crossover():
    parent1 = GenomeConfig("./test_architectures/parent1.save").load()
    print('Parent 1', parent1)
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


def test_xor():
    config = NeatConfig(
        population_size=200,
        inputs=8,
        outputs=4,
        weight_range=(0, 1),
        number_of_tests=10
    )
    neat = XorNeat(config)
    neat.run(500)
    best, fitness = neat.overall_best_performer
    plot_genome(best, filename='./test_plots_xor/overall_best_performer',
                show_disabled=False)
    a = 10#random.randint(0, 100)
    b = 12#random.randint(0, 100)
    expected = a ^ b
    expected_bin = dec_to_bin(expected)
    actual_bin = best.calculate_result(*dec_to_bin(a)[:4], *dec_to_bin(b)[:4])
    actual_bin2 = [1 if a > 0.5 else 0 for a in actual_bin]
    actual1, actual2 = 0, 0
    n = len(actual_bin2)
    for a1, a2 in zip(actual_bin, actual_bin2):
        actual1 += 2 ** (n - 1) * a1
        actual2 += 2 ** (n - 1) * a2
        n -= 1
    # print(neat.fitness_function([1,1],[0], best.hidden_node_count))
    # print(neat.fitness_function([1,1],[1], best.hidden_node_count))
    # print(neat.fitness_function([1,1],[2], best.hidden_node_count))
    # print(neat.fitness_function([a, b], [actual]))
    print(
        f"Fitness of Overall Best Performer {fitness}")
    print(f"Expected: {expected_bin} = {expected}\nActual raw bin: {actual_bin}\nActual processed bin: {actual_bin2} \nActual raw dec: {actual1}\nActual processed dec: {actual2}")
    # print(best.node_genes, best.connection_genes)
    neat.graph()

def test_equation():
    config = NeatConfig(
        population_size=300,    # initial population size
        inputs=2,               # number of inputs
        outputs=1,              # number of outputs
        weight_range=(0, 1),    # initial weight range
        number_of_tests=20      # number of tests for every fitness test
    )
    neat = EquationNeat(config)
    neat.run(500)
    best, fitness = neat.overall_best_performer
    plot_genome(best, filename='./test_plots_equation/overall_best_performer',
                show_disabled=False)
    a = 2#random.randint(0, 100)
    b = 3#random.randint(0, 100)
    expected = 2 * a + b
    actual = best.calculate_result(a, b)[0]
    print(neat.fitness_function([1,1],[0], best.hidden_node_count))
    print(neat.fitness_function([1,1],[1], best.hidden_node_count))
    print(neat.fitness_function([1,1],[2], best.hidden_node_count))
    # print(neat.fitness_function([a, b], [actual]))
    print(
        f"Fitness of Overall Best Performer {fitness}")
    print(f"Expected: {expected}\nActual: {actual}")
    # print(best.node_genes, best.connection_genes)
    neat.graph()

if __name__ == '__main__':
    test_xor()