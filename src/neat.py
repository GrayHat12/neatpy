import math
import random
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional, Callable

from src.genome import Genome
# from src.state import State
from src.connection_gene import ConnectionGene
from src.node_gene import NodeGene
from utils.visualize import plot_genome
from utils.helpers import normalize_value
from utils.enums import NodeType

import matplotlib.pyplot as plt
import numpy as np


@dataclass
class NeatConfig:

    population_size: int = 100
    inputs: int = 2
    outputs: int = 1
    weight_range: Tuple[float, float] = (-1, 1)
    number_of_tests: int = 10


class Neat:
    def __init__(self, config: NeatConfig):
        if not isinstance(config, NeatConfig):
            raise TypeError("config must be of type NeatConfig")
        self.__population = [Genome() for i in range(config.population_size)]
        self.__config = config
        self.__population = self.__initialise__(self.__population)
        self.__generation = 1
        self.__running = False
        self.__best_performer: Optional[Tuple[Genome, float]] = None
        self.__worst_performer: Optional[Tuple[Genome, float]] = None
        self.__average_performer: Optional[Tuple[Genome, float]] = None
        self.__overall_best_performer: Optional[Tuple[Genome, float]] = None
        self.__generation_graph: Dict[int: Dict[str, float]] = {}

    @property
    def generation(self):
        return self.__generation

    @property
    def populations_result_functions(self):
        return [genome.calculate_result for genome in self.__population]

    @property
    def overall_best_performer(self):
        if self.__overall_best_performer:
            return self.__overall_best_performer
        return None
    
    @property
    def population(self):
        return len(self.__population)

    @property
    def best_performer(self):
        return self.__best_performer

    @property
    def worst_performer(self):
        return self.__worst_performer

    @property
    def average_performer(self):
        return self.__average_performer

    def fitness_function(self, inputs: List[float], outputs: List[float], hidden_nodes: int):
        """
        Override this function
        This sample fitness functions expects 2 inputs and expects xor in outputs and returns the fitness accordingly
        """
        a, b = inputs
        output: float = a ^ b
        difference = (abs(output - outputs[0])) * (1 + math.pow(hidden_nodes, 0.5))
        return 1 / (1 + difference)

    def random_input(self):
        """
        Override this function
        This sample function returns random xor input
        """
        a = random.randint(0, 10)
        b = random.randint(0, 10)
        return [a, b]

    def calculate_fitness(self, calculate_output: Callable[..., List[float]], hidden_nodes: int):
        inputs = self.random_input()
        return self.fitness_function(inputs, calculate_output(*inputs), hidden_nodes)

    def every_generation(self):
        """
        Override this function
        This function is called every generation
        """
        print('='*20)
        print(f"Generation: {self.generation}")
        if self.best_performer:
            print(
                f"Best performer: {self.best_performer[1]}")
            plot_genome(self.best_performer[0],
                        filename=f"./test_plots/{self.generation}_best", show_disabled=True)
        if self.worst_performer:
            print(
                f"Worst performer: {self.worst_performer[1]}")
            plot_genome(self.worst_performer[0],
                        filename=f"./test_plots/{self.generation}_worst", show_disabled=True)
        if self.average_performer:
            print(
                f"Average performer: {self.average_performer[1]}")
            plot_genome(self.average_performer[0],
                        filename=f"./test_plots/{self.generation}_average", show_disabled=True)
        print('\n'*2)

    def __initialise__(self, genomes: List[Genome]):
        inputs = [NodeGene(i+1, node_type=NodeType.INPUT) for i in range(self.__config.inputs)]
        outputs = [NodeGene(i+1+self.__config.inputs, node_type=NodeType.OUTPUT) for i in range(self.__config.outputs)]
        # connections:List[ConnectionGene] = []
        for genome in genomes:
            for input_node in inputs:
                genome.add_node(input_node.copy())
            for output_node in outputs:
                genome.add_node(output_node.copy())
                for input_node in inputs:
                    genome.create_connection(
                        input_node.innovation_number,
                        output_node.innovation_number,
                    )
        return genomes

    def __iteration(self):
        genome_fitness: Dict[Genome, float] = {}
        new_generation: List[Genome] = []
        species_graph:Dict[str, dict] = {}
        fitness_sum = 0
        # print('total nodes', len(state.nodes))
        # print('total connections', len(state.connections))
        least_fit = math.inf
        most_fit = -math.inf
        test_input = [self.random_input() for _ in range(self.__config.number_of_tests)]
        for genome in self.__population:
            genome.remove_useless_leafs()
            fitness = [self.fitness_function(test_inp, genome.calculate_result(*test_inp), genome.hidden_node_count) for test_inp in test_input]
            fitness = sum(fitness) / len(fitness)
            if fitness < least_fit:
                least_fit = fitness
            if fitness > most_fit:
                most_fit = fitness
            genome_fitness[genome] = fitness
            fitness_sum += fitness
            species_str = f"Species_{len(genome.node_genes)}"
            if species_str not in species_graph:
                species_graph[species_str] = {
                    'count': 0,
                    'best_fit': fitness,
                    'worst_fit': fitness,
                }
            species_graph[species_str]['count'] += 1
            if fitness > species_graph[species_str]['best_fit']:
                species_graph[species_str]['best_fit'] = fitness
            if fitness < species_graph[species_str]['worst_fit']:
                species_graph[species_str]['worst_fit'] = fitness


        # select parents for baby
        parents: List[Tuple[Genome, float]] = []
        # print('fitness sum', fitness_sum)
        # Comment below stuff to disable crossover
        while len(parents) < 0.1 * len(self.__population):
            parent = self._select_parent(fitness_sum, genome_fitness)
            if parent not in parents:
                parents.append(parent)

        while len(parents) > 0:
            if len(parents) > 1:
                parent_a = random.choice(parents)
                parents.remove(parent_a)
                parent_b = random.choice(parents)
                parents.remove(parent_b)
            else:
                parent_a = parents[0]
                parents.remove(parent_a)
                parent_b = (parent_a[0].copy(), parent_a[1])
            more_fit = parent_a if parent_a[1] > parent_b[1] else parent_b
            less_fit = parent_a if more_fit == parent_b else parent_b
            baby = Genome.crossover(
                more_fit[0], less_fit[0], equal_fitness=parent_a[1] == parent_b[1])
            baby.mutate()
            new_generation.append(baby)

        genome_sorted = sorted(genome_fitness.items(),
                               key=lambda x: x[1], reverse=True)
        # print('genome sorted', genome_sorted)
        self.__best_performer = (genome_sorted[0][0], genome_sorted[0][1])
        self.__worst_performer = (genome_sorted[-1][0], genome_sorted[-1][1])
        # one_fourth_fitness = genome_sorted[len(genome_sorted) // 4][1]
        self.__average_performer = (genome_sorted[len(genome_sorted) // 2][0], genome_sorted[len(genome_sorted) // 2][1])
        if (self.__overall_best_performer and self.__best_performer[1] >= self.__overall_best_performer[1]) or self.__overall_best_performer is None:
            self.__overall_best_performer = (
                self.__best_performer[0], self.__best_performer[1])

        self.__generation_graph[self.generation] = {
            'best': self.__best_performer[1],
            'worst': self.__worst_performer[1],
            'average': self.__average_performer[1],
            'species': species_graph,
        }

        # kill 20% of population
        genome_sorted = genome_sorted[:-int(0.2 * len(genome_sorted))]

        for i, (genome, fitness) in enumerate(genome_sorted):
            # print("Genome", genome, "conns", [conn.weight for conn in genome.connection_genes])
            _genome = genome.copy()
            if i > (0.1 * self.__config.population_size):
                _genome.mutate()
            # _genome.mutate()
            new_generation.append(_genome)
            if len(new_generation) >= self.__config.population_size:
                break

        # input_nodes = [node.innovation_number for node in state.nodes if node.node_type == NodeType.INPUT]
        # output_nodes = [node.innovation_number for node in state.nodes if node.node_type == NodeType.OUTPUT]

        while len(new_generation) < self.__config.population_size:
            random_baby = [Genome()]
            random_baby = self.__initialise__(random_baby)
            random_baby[0].mutate()
            new_generation.append(random_baby[0])
        

        # mutate babies
        # for baby in new_generation:
        #     baby.mutate()

        self.__generation += 1
        self.__population = new_generation

    def _select_parent(self, fitness_sum: float, genome_fitness: Dict[Genome, float]):
        lucky_number = random.uniform(0, fitness_sum)
        running_sum = 0
        for genome, fitness in genome_fitness.items():
            running_sum += fitness
            if running_sum >= lucky_number:
                return genome, fitness

    def run(self, iterations: int):
        if self.__running:
            return
        self.__running = True
        for i in range(iterations):
            self.every_generation()
            self.__iteration()

    def graph(self):
        best = []
        average = []
        worst = []
        generations = []
        species_graph = {}
        # with open("results.json", "w+", encoding="utf-8") as f:
        #     import json
        #     json.dump(self.__generation_graph, f)
        for generation in self.__generation_graph:
            best.append(self.__generation_graph[generation]['best'])
            average.append(self.__generation_graph[generation]['average'])
            worst.append(self.__generation_graph[generation]['worst'])
            generations.append(generation)
            for species_key in self.__generation_graph[generation]['species']:
                if species_key not in species_graph:
                    species_graph[species_key] = {
                        'count': [],
                        'best_fit': [],
                        'worst_fit': [],
                    }
        
        for species_key in species_graph:
            for generation in self.__generation_graph:
                if species_key in self.__generation_graph[generation]['species']:
                    species_graph[species_key]['count'].append(self.__generation_graph[generation]['species'][species_key]['count'])
                    species_graph[species_key]['best_fit'].append(self.__generation_graph[generation]['species'][species_key]['best_fit'])
                    species_graph[species_key]['worst_fit'].append(self.__generation_graph[generation]['species'][species_key]['worst_fit'])
                else:
                    species_graph[species_key]['count'].append(0)
                    species_graph[species_key]['best_fit'].append(0)
                    species_graph[species_key]['worst_fit'].append(0)

        max_num = max(best + average + worst)
        min_num = min(best + average + worst)

        best = [normalize_value(x, min_num, max_num, range=(0, 1))
                for x in best]
        average = [normalize_value(x, min_num, max_num, range=(0, 1))
                   for x in average]
        worst = [normalize_value(x, min_num, max_num, range=(0, 1))
                 for x in worst]

        # fitness graph
        plt.figure()
        plt.plot(generations, best, label='best', color='green')
        plt.plot(generations, average, label='middle',color='yellow')
        plt.plot(generations, worst, label='worst', color='red')
        plt.xticks(np.linspace(0, self.generation, 10))
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        # plt.ylim(0, max(best))
        plt.legend()

        # species graph
        plt.figure()
        labels = []
        counts = []
        sorted_species = sorted(species_graph.items(), key=lambda x: x[1]['count'].count(0))
        for label, species in sorted_species[:5]:
            labels.append(label)
            counts.append(species['count'])
        plt.stackplot(
            generations,
            counts,
            labels=labels,
        )
        
        plt.xlabel('Generation')
        plt.ylabel('Species Count')
        plt.xticks(np.linspace(0, self.generation, 10))
        plt.legend()

        plt.show()

        print(self.__generation_graph[self.generation-1]['species'])
