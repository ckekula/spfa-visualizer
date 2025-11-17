import pygame
from visualizer import Visualizer
from algorithms import SPFA_Algorithms

# CONFIG
ROWS = 10
COLS = 10
CELL_SIZE = 40
GRID_ORIGIN = (50, 50)

# Initialize maze and demo walls (0 = path, 1 = wall)
maze = [[0 for _ in range(COLS)] for _ in range(ROWS)]
maze[1][1] = 1
maze[2][1] = 1
maze[3][1] = 1
maze[1][3] = 1
maze[2][3] = 1
maze[3][3] = 1
maze[4][2] = 1
maze[5][2] = 1
maze[6][2] = 1
maze[4][9] = 1
maze[5][9] = 1
maze[6][9] = 1

# Specify start & end
start = (0, 0)  # (row, col)
end   = (9, 9)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("SPFA Visualizer")

    font = pygame.font.SysFont(None, 20)

    # Create Visualizer (holds maze, drawing and helpers)
    viz = Visualizer(rows=ROWS, cols=COLS, cell_size=CELL_SIZE,
                     grid_origin=GRID_ORIGIN, maze=maze, start=start, end=end)

    # Create graph from maze
    graph = viz.maze_to_graph()
    graph.start = start
    graph.goal = end

    print(f"Graph has {len(graph.nodes)} nodes")
    print(f"Start node {start} neighbors: {graph.neighbors(start)}")
    print(f"End node {end} neighbors: {graph.neighbors(end)}")

    # -------- Convert graph to Dijkstra edges (prepare once) --------
    edges = []   # (u,v,w)

    for (r, c) in graph.nodes:
        u = viz.id_from_coord(r, c)
        for (nr, nc) in graph.neighbors((r, c)):
            v = viz.id_from_coord(nr, nc)
            edges.append((u, v, 1))

    src_id = viz.id_from_coord(*start)
    dst_id = viz.id_from_coord(*end)

    # IMPORTANT: n must match numeric ID range (0..ROWS*COLS-1)
    n = ROWS * COLS

    # UI state
    shortest_path = []  # initially nothing — only start/end are visible
    selected_algo = "Dijkstra"  # hardcoded selection options: "Dijkstra", "SPFA" (if implemented)

    # UI elements (simple buttons)
    find_button = pygame.Rect(600, 50, 150, 40)
    algo_buttons = [
    (pygame.Rect(600, 110, 150, 30), "Dijkstra"),
    (pygame.Rect(600, 150, 150, 30), "A*"),
    (pygame.Rect(600, 190, 150, 30), "Bellman-Ford"),
]


    def compute_shortest_path(algo_name):        
        nonlocal shortest_path
        print(f"Computing path using: {algo_name}")

        def manhattan_heuristic(node_id):
            r, c = viz.coord_from_id(node_id)
            er, ec = end
            return abs(r - er) + abs(c - ec)
        
        try:
            if algo_name == "Dijkstra":
                path_ids = SPFA_Algorithms.dijkstras(n=n, edges=edges, src=src_id, dst=dst_id)
            elif algo_name == "A*":
                path_ids = SPFA_Algorithms.a_star( n=n, edges=edges, src=src_id, dst=dst_id, heuristic=manhattan_heuristic)
            
            elif algo_name == "Bellman-Ford":
                path_ids = SPFA_Algorithms.bellman_ford(n=n, edges=edges, src=src_id, dst=dst_id)
            else:
                print(f"Unknown algorithm: {algo_name}")
                return

            shortest_path = [viz.coord_from_id(pid) for pid in path_ids]
            print(f"Found path length: {len(shortest_path)}")
        
        except Exception as e:
            print("Error computing path:", e)

    # Main Loop
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Find button clicked -> compute shortest path with selected algorithm
                if find_button.collidepoint(mx, my):
                    compute_shortest_path(selected_algo)

                # Algorithm selection buttons
                for rect, name in algo_buttons:
                    if rect.collidepoint(mx, my):
                        selected_algo = name
                        print(f"Selected algorithm: {selected_algo}")

        screen.fill((50, 50, 50))

        # Draw grid (start & end will be visible even when shortest_path is empty)
        viz.draw_grid(screen, path=shortest_path)

        # Draw UI panel
        pygame.draw.rect(screen, (30, 30, 30), (580, 30, 190, 200))
        pygame.draw.rect(screen, (70, 130, 180), find_button)
        screen.blit(font.render("Find Path", True, (255, 255, 255)), (find_button.x + 20, find_button.y + 10))

        # Algorithm buttons
        for rect, name in algo_buttons:
            color = (100, 100, 100)
            if name == selected_algo:
                color = (100, 180, 100)
            pygame.draw.rect(screen, color, rect)
            screen.blit(font.render(name, True, (255, 255, 255)), (rect.x + 10, rect.y + 7))

        # Show currently selected algorithm text
        screen.blit(font.render(f"Selected: {selected_algo}", True, (220, 220, 220)), (600, 200))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()