from graph import Graph
import pygame

class MazeVisualizer:
    def __init__(self, rows=10, cols=10, cell_size=40, grid_origin=(50,50),
                 maze=None, start=(0,0), end=None):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.grid_origin = grid_origin

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.START_COLOR = (0, 255, 0)
        self.END_COLOR = (255, 0, 0)
        self.GRID_LINE = (180, 180, 180)
        self.PATH_COLOR = (0, 0, 255)

        # Maze (0 = path, 1 = wall). If not provided, initialize empty.
        if maze is None:
            self.maze = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        else:
            self.maze = maze

        self.start = start
        self.end = end if end is not None else (self.rows - 1, self.cols - 1)

    def id_from_coord(self, r, c):
        return r * self.cols + c

    def coord_from_id(self, id_):
        return (id_ // self.cols, id_ % self.cols)

    def draw_grid(self, surface, path=None):
        ox, oy = self.grid_origin

        for r in range(self.rows):
            for c in range(self.cols):
                # path coloring has highest priority
                if path and (r, c) in path:
                    color = self.PATH_COLOR
                elif (r, c) == self.start:
                    color = self.START_COLOR
                elif (r, c) == self.end:
                    color = self.END_COLOR
                else:
                    color = self.BLACK if self.maze[r][c] == 1 else self.WHITE

                rect = pygame.Rect(
                    ox + c * self.cell_size,
                    oy + r * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, self.GRID_LINE, rect, 1)

    def maze_to_graph(self):
        """Convert maze to graph where white cells are nodes connected orthogonally."""
        g = Graph()

        # Create a node for each white cell
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze[r][c] == 0:  # white path cell
                    node_id = (r, c)
                    g.add_node(node_id, x=c, y=r)

        # Connect orthogonal neighbors (no diagonals)
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze[r][c] == 0:  # current cell is white
                    current = (r, c)

                    # Check all 4 orthogonal directions
                    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr][nc] == 0:
                            neighbor = (nr, nc)
                            g.add_edge(current, neighbor)

        return g


class MazeState:
    """Manages the maze grid and start/end positions"""
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.maze = [[0 for _ in range(cols)] for _ in range(rows)]
        self.start = None
        self.end = None
        self.shortest_path = []
    
    def toggle_wall(self, row, col):
        """Toggle wall at given position"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.maze[row][col] = 1 - self.maze[row][col]
            self.shortest_path = []
    
    def set_start(self, row, col):
        """Set start position and ensure it's not a wall"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.start = (row, col)
            self.maze[row][col] = 0
            self.shortest_path = []
    
    def set_end(self, row, col):
        """Set end position and ensure it's not a wall"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.end = (row, col)
            self.maze[row][col] = 0
            self.shortest_path = []
    
    def clear(self):
        """Reset maze to empty state"""
        self.maze = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.end = None
        self.shortest_path = []


class UIState:
    """Manages UI state and button definitions"""
    def __init__(self):
        self.selected_algo = "Dijkstra"
        self.edit_mode = "wall"
        self.error_message = ""
        self.error_timer = 0
        
        # Button definitions
        self.find_button = pygame.Rect(600, 50, 150, 40)
        self.clear_button = pygame.Rect(600, 100, 150, 40)
        
        self.algo_buttons = [
            (pygame.Rect(600, 160, 150, 30), "Dijkstra"),
            (pygame.Rect(600, 200, 150, 30), "A*"),
            (pygame.Rect(600, 240, 150, 30), "Bellman-Ford"),
        ]
        
        self.mode_buttons = [
            (pygame.Rect(600, 300, 150, 30), "wall", "Toggle Wall"),
            (pygame.Rect(600, 340, 150, 30), "start", "Set Start"),
            (pygame.Rect(600, 380, 150, 30), "end", "Set End"),
        ]
    
    def show_error(self, message):
        """Display error message for 3 seconds"""
        self.error_message = message
        self.error_timer = 180  # 3 seconds at 60 FPS
    
    def update_error_timer(self):
        """Decrease error timer"""
        if self.error_timer > 0:
            self.error_timer -= 1