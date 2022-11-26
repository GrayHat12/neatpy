from typing import List
import random
import math
from src.neat import Neat, NeatConfig
from utils.visualize import plot_genome


class XorNeat(Neat):
    def __init__(self, config: NeatConfig):
        super().__init__(config)

    def fitness_function(self, inputs: List[float], outputs: List[float], hidden_nodes: int):
        a1, a2, a3, a4, b1, b2, b3, b4 = inputs
        c1, c2, c3, c4 = outputs
        c1 = 1 if c1 > 0.5 else 0
        c2 = 1 if c2 > 0.5 else 0
        c3 = 1 if c3 > 0.5 else 0
        c4 = 1 if c4 > 0.5 else 0
        number1 = a1 * 8 + a2 * 4 + a3 * 2 + a4
        number2 = b1 * 8 + b2 * 4 + b3 * 2 + b4
        output: float = number1 ^ number2
        output_from_network = c1 * 8 + c2 * 4 + c3 * 2 + c4
        difference = ((output - output_from_network)** 2) * (1 + math.pow(hidden_nodes, 0.5))
        return 1 / (1 + difference)

    def random_input(self):
        # return [1,0]
        return [
            random.choice([0, 1]),
            random.choice([0, 1]),
            random.choice([0, 1]),
            random.choice([0, 1]),

            random.choice([0, 1]),
            random.choice([0, 1]),
            random.choice([0, 1]),
            random.choice([0, 1]),
        ]

    def every_generation(self):
        print('='*20)
        print(f"Generation: {self.generation}, Population {self.population}")
        save_plot = self.generation % 50 == 0
        if self.best_performer:
            print(
                f"Best performer: {self.best_performer[1]}")
            if save_plot:
                plot_genome(self.best_performer[0],
                            filename=f"./test_plots/{self.generation}_best", show_disabled=True)
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
