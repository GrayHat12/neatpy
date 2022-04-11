from graphviz import Digraph
from utils.enums import NodeType
from src.genome import Genome
import copy


def plot_genome(genome: Genome, view=False, filename='test', node_names=None, show_disabled=True, prune_unused=False,
                node_colors=None, fmt='svg'):
    """ Receives a genome and draws a neural network with arbitrary topology. """

    if node_names is None:
        node_names = {}

    assert type(node_names) is dict

    if node_colors is None:
        node_colors = {}

    assert type(node_colors) is dict

    node_attrs = {
        'shape': 'circle',
        'fontsize': '9',
        'height': '0.2',
        'width': '0.2'
    }

    dot = Digraph(format=fmt, node_attr=node_attrs)

    inputs = set()
    for k in genome.node_genes:
        if k.node_type is not NodeType.INPUT:
            continue
        inputs.add(k)
        name = node_names.get(k, str(k))
        input_attrs = {'style': 'filled', 'shape': 'box',
                       'fillcolor': node_colors.get(k, 'lightgray')}
        dot.node(name, _attributes=input_attrs)

    outputs = set()
    for k in genome.node_genes:
        if k.node_type is not NodeType.OUTPUT:
            continue
        outputs.add(k)
        name = node_names.get(k, str(k))
        node_attrs = {'style': 'filled',
                      'fillcolor': node_colors.get(k, 'lightblue')}

        dot.node(name, _attributes=node_attrs)

    if prune_unused:
        connections = set()
        for cg in genome.connection_genes:
            if cg.enabled or show_disabled:
                connections.add((cg.from_node, cg.to_node))

        used_nodes = copy.copy(outputs)
        pending = copy.copy(outputs)
        while pending:
            new_pending = set()
            for a, b in connections:
                if b in pending and a not in used_nodes:
                    new_pending.add(a)
                    used_nodes.add(a)
            pending = new_pending
    else:
        used_nodes = set(genome.node_genes)

    for n in used_nodes:
        if n in inputs or n in outputs:
            continue

        attrs = {'style': 'filled',
                 'fillcolor': node_colors.get(n, 'white')}
        dot.node(str(n), _attributes=attrs)

    for cg in genome.connection_genes:
        if cg.enabled or show_disabled:
            # if cg.input not in used_nodes or cg.output not in used_nodes:
            #    continue
            input, output = cg.from_node, cg.to_node
            a = node_names.get(input, str(input))
            b = node_names.get(output, str(output))
            style = 'solid' if cg.enabled else 'dotted'
            color = 'green' if cg.weight > 0 else 'red'
            width = str(0.1 + abs(cg.weight))
            dot.edge(a, b, _attributes={
                     'style': style, 'color': color, 'penwidth': width})

    dot.render(filename, format='svg', view=view, cleanup=True)
