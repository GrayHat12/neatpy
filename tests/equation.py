from typing import List, Callable

from src.neat import Neat, NeatConfig
from utils.visualize import plot_genome

from typing import List
import random
import math

from src.neat import Neat, NeatConfig
from utils.visualize import plot_genome


class EquationNeat(Neat):
    def __init__(self, config: NeatConfig):
        super().__init__(config)

    def fitness_function(self, inputs: List[float], outputs: List[float], hidden_nodes: int):
        """
        Equation: 2x + y
        """
        a, b = inputs
        output = 2 * a + b
        difference = ((output - outputs[0]) ** 2) * (1 + math.pow(hidden_nodes, 0.5))
        return 1 / (1 + difference)
    
    def random_input(self):
        return [random.uniform(0, 1), random.uniform(0, 1)]

    def calculate_fitness(self, calculate_output: Callable[..., List[float]], hidden_nodes: int):
        return super().calculate_fitness(calculate_output, hidden_nodes)
    
    def every_generation(self):
        print('='*20)
        print(f"Generation: {self.generation}, Population {self.population}")
        save_plot = self.generation % 50 == 0
        if self.best_performer:
            print(f"Best performer: {self.best_performer[1]}")
            if save_plot:
                plot_genome(self.best_performer[0], filename=f"./test_plots/{self.generation}_best", show_disabled=True)
        if self.worst_performer:
            print(
                f"Worst performer: {self.worst_performer[1]}")
            if save_plot:
                plot_genome(self.worst_performer[0],
                        filename=f"./test_plots/{self.generation}_worst", show_disabled=True)
        if self.average_performer:
            print(
                f"Middle performer: {self.average_performer[1]}")
            if save_plot:
                plot_genome(self.average_performer[0],
                        filename=f"./test_plots/{self.generation}_average", show_disabled=True)
        print('\n'*2)