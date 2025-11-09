from graph import Graph

def dfs(graph, start):
    # implementation of dfs algorithm
    return

def main():
    g = Graph()
    for id, (x, y) in {
        "A": (0, 0), "B": (1, 0), "C": (1, 1), "D": (0, 1)
    }.items():
        g.add_node(id, x, y)

    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("C", "D")
    g.add_edge("D", "A")

    g.start = "A"
    g.goal = "C"

    print("Adjacency list:", g.as_adjacency_list())
    print("Coordinates:", {n: (g.nodes[n].x, g.nodes[n].y) for n in g.nodes})

if __name__ == "__main__":
    main()