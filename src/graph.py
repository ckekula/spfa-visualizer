class Node:
    def __init__(self, id, x=0, y=0):
        self.id = id
        self.x = x
        self.y = y
        self.neighbors = set()  # store neighbor IDs

class Graph:
    def __init__(self):
        self.nodes = {}  # {id: Node}
        self.start = None
        self.goal = None

    def add_node(self, id, x=0, y=0):
        self.nodes[id] = Node(id, x, y)

    def add_edge(self, a, b):
        if a in self.nodes and b in self.nodes:
            self.nodes[a].neighbors.add(b)
            self.nodes[b].neighbors.add(a)

    def remove_edge(self, a, b):
        self.nodes[a].neighbors.discard(b)
        self.nodes[b].neighbors.discard(a)

    def remove_node(self, id):
        if id in self.nodes:
            for n in self.nodes[id].neighbors:
                self.nodes[n].neighbors.discard(id)
            del self.nodes[id]

    def neighbors(self, id):
        return list(self.nodes[id].neighbors)

    def as_adjacency_list(self):
        return {nid: list(node.neighbors) for nid, node in self.nodes.items()}
