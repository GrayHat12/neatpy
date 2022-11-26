from typing import List

from src.connection_gene import ConnectionGene
from src.gene_store import CONNECTION_GENE_STORE, NODE_GENE_STORE, get_connection_innovation_number
from src.genome import Genome
import re
from src.node_gene import NodeGene

from utils.enums import NodeType, Task


class Command:
    def __init__(self, task: Task, connection_innovation=None, from_innovation=None, to_innovation=None, connection_weight=None, from_weight=None, to_weight=None, connection_enabled=None):
        self.task = task
        self.connection_innovation = connection_innovation
        self.from_innovation = from_innovation
        self.to_innovation = to_innovation
        self.connection_weight = connection_weight
        self.from_weight = from_weight
        self.to_weight = to_weight
        self.connection_enabled = connection_enabled

    def execute_connection_mutation(self, genome: Genome) -> Genome:
        from_node = genome.node_genes.index(NodeGene(self.from_innovation))
        to_node = genome.node_genes.index(NodeGene(self.to_innovation))
        if isinstance(self.from_weight, float):
            genome.node_genes[from_node]._weight = self.from_weight
        if isinstance(self.to_weight, float):
            genome.node_genes[to_node]._weight = self.to_weight
        genome.connection_mutation((
            genome.node_genes[from_node],
            genome.node_genes[to_node]
        ))
        if isinstance(self.connection_weight, float):
            genome.connection_genes[-1]._weight = self.connection_weight
        if isinstance(self.connection_enabled, bool):
            if genome.connection_genes[-1].enabled != self.connection_enabled:
                genome.connection_genes[-1].mutate_enabled()
        if isinstance(self.connection_innovation,int):
            genome.connection_genes[-1]._INNOVATION_NUMBER = self.connection_innovation
        return genome

    def execute_node_mutation(self, genome: Genome) -> Genome:
        connection = None
        for con in genome.connection_genes:
            if con.from_node.innovation_number == self.from_innovation and con.to_node.innovation_number == self.to_innovation:
                connection = con
                break
        if connection is None:
            raise Exception(f"Connection not found for node mutation")
        genome.node_mutation(genome.connection_genes[genome.connection_genes.index(connection)])
        if isinstance(self.connection_weight, float):
            genome.connection_genes[connection]._weight = self.connection_weight
        if isinstance(self.connection_enabled, bool):
            if genome.connection_genes[connection].enabled != self.connection_enabled:
                genome.connection_genes[connection].mutate_enabled()
        return genome

    def execute_connection_update(self, genome: Genome) -> Genome:
        if not self.connection_innovation:
            self.connection_innovation = get_connection_innovation_number(self.from_innovation, self.to_innovation)
        # print('connection update for',self.connection_innovation)
        connection = genome.connection_genes.index(ConnectionGene(
            None, None, self.connection_innovation, enabled=self.connection_enabled, weight=self.connection_weight))
        if isinstance(self.connection_weight, float):
            genome.connection_genes[connection]._weight = self.connection_weight
        if isinstance(self.connection_enabled, bool):
            if genome.connection_genes[connection].enabled != self.connection_enabled:
                genome.connection_genes[connection].mutate_enabled()
        if isinstance(self.from_weight, float):
            node = genome.node_genes.index(
                genome.connection_genes[connection].from_node)
            genome.node_genes[node]._weight = self.from_weight
        if isinstance(self.to_weight, float):
            node = genome.node_genes.index(
                genome.connection_genes[connection].to_node)
            genome.node_genes[node]._weight = self.to_weight
        return genome

    def execute(self, genome: Genome) -> Genome:
        if self.task is Task.CONNECTION_MUTATION:
            return self.execute_connection_mutation(genome)
        elif self.task is Task.CONNECTION_UPDATE:
            return self.execute_connection_update(genome)
        elif self.task is Task.NODE_MUTATION:
            return self.execute_node_mutation(genome)
        else:
            raise Exception(f"Invalid task {self.task} assigned")

    def __str__(self) -> str:
        return f"Command({self.task.name},{self.connection_innovation},{self.from_innovation},{self.to_innovation})"

class GenomeConfig:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.contents = None
        self.inputs = []
        self.outputs = []
        self.connections = []
        self.commands: List[Command] = []

    def __get_inputs(self) -> List[str]:
        match = re.search(r'INPUT_NODES=(.*)',
                          self.contents or "", re.MULTILINE)
        if match:
            return match.group(1).split(',')
        raise Exception("Failed to find INPUT_NODES")

    def __get_outputs(self) -> List[str]:
        match = re.search(r'OUTPUT_NODES=(.*)',
                          self.contents or "", re.MULTILINE)
        if match:
            return match.group(1).split(',')
        raise Exception("Failed to find OUTPUT_NODES")

    def __get_connections(self) -> List[str]:
        match = re.search(r'CONNECTIONS=(.*)',
                          self.contents or "", re.MULTILINE)
        if match:
            return match.group(1).split(',')
        raise Exception("Failed to find CONNECTIONS")

    def __process_inputs(self) -> List[int]:
        return [int(i) for i in self.__get_inputs()]

    def __process_outputs(self) -> List[int]:
        return [int(i) for i in self.__get_outputs()]

    def __process_commands(self) -> List[Command]:
        fake_nodes = [*self.inputs, *self.outputs]
        connections = self.__get_connections()
        commands = []
        pending_connections = []
        for connection in connections:
            match = re.search(
                r'(\d+)(\$\d+\.\d+)?:(\d+)(\$\d+\.\d+)?(-|=)(\d+)(\$\d+\.\d+)?', connection)
            if match:
                connection_innovation = int(match.group(1))
                connection_weight = None
                if match.group(2):
                    connection_weight = float(match.group(2)[1:])
                from_innovation = int(match.group(3))
                from_weight = None
                if match.group(4):
                    from_weight = float(match.group(4)[1:])
                connection_enabled = str(match.group(5))
                if connection_enabled == "=":
                    connection_enabled = True
                elif connection_enabled == '-':
                    connection_enabled = False
                else:
                    raise Exception("Failed to parse connection enabled")
                to_innovation = int(match.group(6))
                to_weight = None
                if match.group(7):
                    to_weight = float(match.group(7)[1:])
                if from_innovation not in fake_nodes or to_innovation not in fake_nodes:
                    missing = from_innovation
                    to_ = to_innovation
                    if missing in fake_nodes:
                        missing = to_innovation
                        to_ = from_innovation
                    index = -1
                    for i, pending in enumerate(pending_connections):
                        from_ = None
                        if pending[1] == missing:
                            index = i
                            from_ = pending[2]
                        elif pending[2] == missing:
                            index = i
                            from_ = pending[1]
                        if index >= 0:
                            fake_nodes.append(missing)
                            commands.append(Command(
                                task=Task.NODE_MUTATION,
                                connection_innovation=pending[0],
                                from_innovation=from_,
                                to_innovation=to_,
                                connection_weight=None,
                                from_weight=None,
                                to_weight=None,
                                connection_enabled=None
                            ))
                            commands.append(Command(
                                task=Task.CONNECTION_UPDATE,
                                # connection_innovation=pending[0],
                                from_innovation=pending[1],
                                to_innovation=pending[2],
                                connection_weight=pending[3],
                                from_weight=pending[4],
                                to_weight=pending[5],
                                connection_enabled=pending[6]
                            ))
                            commands.append(Command(
                                task=Task.CONNECTION_UPDATE,
                                # connection_innovation=connection_innovation,
                                from_innovation=pending[1],
                                to_innovation=pending[2],
                                connection_weight=connection_weight,
                                from_weight=from_weight,
                                to_weight=to_weight,
                                connection_enabled=connection_enabled
                            ))
                            break
                    if index < 0:
                        pending_connections.append(
                            [
                                connection_innovation,
                                from_innovation,
                                to_innovation,
                                connection_weight,
                                from_weight,
                                to_weight,
                                connection_enabled
                            ]
                        )
                    else:
                        popped = pending_connections.pop(index)
                else:
                    commands.append(Command(
                        Task.CONNECTION_MUTATION,
                        connection_innovation,
                        from_innovation,
                        to_innovation,
                        connection_weight,
                        from_weight,
                        to_weight,
                        connection_enabled
                    ))
            else:
                raise Exception("Failed to parse connection")
        return commands

    def __load(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.contents = f.read()
        self.inputs = self.__process_inputs()
        self.outputs = self.__process_outputs()
        self.commands = self.__process_commands()

    def load(self) -> Genome:
        self.__load()
        if not isinstance(self.contents, str):
            raise ValueError("Failed Reading File Contents")
        genome = Genome()
        for input in self.inputs:
            genome.add_node_gene(
                NodeGene(input, node_type=NodeType.INPUT)
            )
        for output in self.outputs:
            genome.add_node_gene(
                NodeGene(output, node_type=NodeType.OUTPUT)
            )
        print("Commands",[str(command) for command in self.commands])
        for command in self.commands:
            print(command.__dict__)
            if command.connection_innovation == 8:
                print("HERE")
            print(str(genome))
            print(NODE_GENE_STORE)
            print(CONNECTION_GENE_STORE)
            genome = command.execute(genome)
        print(str(genome))
        return genome

    def save(self, genome: Genome):
        output = ""
        input_nodes = []
        output_nodes = []
        for node in genome.node_genes:
            if node.node_type == NodeType.INPUT:
                input_nodes.append(str(node.innovation_number))
            if node.node_type == NodeType.OUTPUT:
                output_nodes.append(str(node.innovation_number))
        output += f"INPUT_NODES={','.join(input_nodes)}\n"
        output += f"OUTPUT_NODES={','.join(output_nodes)}\n"
        connections = []
        for connection in genome.connection_genes:
            connections.append(
                f"{connection.innovation_number}${connection.weight}:{connection.from_node.innovation_number}${connection.from_node.weight}{'=' if connection.enabled else '-'}{connection.to_node.innovation_number}${connection.to_node.weight}"
            )
        output += f"CONNECTIONS={','.join(connections)}\n"

        with open(self.filepath, 'w+', encoding='utf-8') as f:
            f.write(output)
        return
