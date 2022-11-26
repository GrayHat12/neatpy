CONNECTION_GENE_STORE = {}
NODE_GENE_STORE = {}


def update_connection_gene_store(from_node: int, to_node: int, value: int):
    CONNECTION_GENE_STORE.update({
        f'{from_node}_{to_node}': value
    })


def get_next_node_innovation_number() -> int:
    value = max(list(NODE_GENE_STORE.values())+[0]) + 1
    return value

def update_node_gene_store(value: int):
    if value not in list(NODE_GENE_STORE.values()):
        NODE_GENE_STORE.update({
            f'STATIC_{len(NODE_GENE_STORE.keys())}': value
        })


def get_connection_innovation_number(from_node: int, to_node: int) -> int:
    key = f"{from_node}_{to_node}"
    if key in CONNECTION_GENE_STORE:
        return CONNECTION_GENE_STORE.get(key)
    value = max(list(CONNECTION_GENE_STORE.values()) + [0]) + 1
    CONNECTION_GENE_STORE.update({
        key: value
    })
    return value


def get_node_innovation_number(from_node: int, to_node: int) -> int:
    key = f"{from_node}_{to_node}"
    if key in NODE_GENE_STORE:
        return NODE_GENE_STORE.get(key)
    value = max(list(NODE_GENE_STORE.values())+[0]) + 1
    NODE_GENE_STORE.update({
        key: value
    })
    return value
