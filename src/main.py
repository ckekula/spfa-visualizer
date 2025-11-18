import pygame
from maze import MazeVisualizer, MazeState, UIState
from algorithms import PathFinder

# CONFIG
ROWS = 10
COLS = 10
CELL_SIZE = 40
GRID_ORIGIN = (50, 50)


class SPFAVisualizer:
    """Main application class"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("SPFA Visualizer - Interactive")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont(None, 20)
        self.error_font = pygame.font.SysFont(None, 18)
        
        # Initialize state components
        self.maze_state = MazeState(ROWS, COLS)
        self.ui_state = UIState()
        
        # Initialize visualizer
        self.viz = MazeVisualizer(
            rows=ROWS, cols=COLS, cell_size=CELL_SIZE,
            grid_origin=GRID_ORIGIN, maze=self.maze_state.maze,
            start=None, end=None
        )
        
        # Initialize pathfinder
        self.pathfinder = PathFinder(self.viz, self.maze_state)
        
        self.running = True
    
    def handle_grid_click(self, mx, my):
        """Handle clicks on the maze grid"""
        gx = mx - GRID_ORIGIN[0]
        gy = my - GRID_ORIGIN[1]
        
        if gx < 0 or gy < 0:
            return
        
        col = gx // CELL_SIZE
        row = gy // CELL_SIZE
        
        if 0 <= row < ROWS and 0 <= col < COLS:
            if self.ui_state.edit_mode == "wall":
                self.maze_state.toggle_wall(row, col)
                print(f"Toggled wall at ({row}, {col})")
            elif self.ui_state.edit_mode == "start":
                self.maze_state.set_start(row, col)
                print(f"Start set to ({row}, {col})")
            elif self.ui_state.edit_mode == "end":
                self.maze_state.set_end(row, col)
                print(f"End set to ({row}, {col})")
    
    def handle_button_clicks(self, mx, my):
        """Handle clicks on UI buttons"""
        # Find Path button
        if self.ui_state.find_button.collidepoint(mx, my):
            try:
                self.pathfinder.compute_path(self.ui_state.selected_algo)
            except ValueError as e:
                self.ui_state.show_error(f"Error: {str(e)}")
            except Exception as e:
                self.ui_state.show_error(f"Error: {str(e)}")
                print("Error computing path:", e)
            return True
        
        # Clear Maze button
        if self.ui_state.clear_button.collidepoint(mx, my):
            self.maze_state.clear()
            print("Maze cleared")
            return True
        
        # Algorithm selection buttons
        for rect, name in self.ui_state.algo_buttons:
            if rect.collidepoint(mx, my):
                self.ui_state.selected_algo = name
                print(f"Selected algorithm: {name}")
                return True
        
        # Edit mode buttons
        for rect, mode, _ in self.ui_state.mode_buttons:
            if rect.collidepoint(mx, my):
                self.ui_state.edit_mode = mode
                print(f"Edit mode: {mode}")
                return True
        
        return False
    
    def handle_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                
                # Check grid clicks first
                grid_rect = pygame.Rect(
                    GRID_ORIGIN[0], GRID_ORIGIN[1],
                    COLS * CELL_SIZE, ROWS * CELL_SIZE
                )
                if grid_rect.collidepoint(mx, my):
                    self.handle_grid_click(mx, my)
                else:
                    self.handle_button_clicks(mx, my)
    
    def draw_ui(self):
        """Draw all UI elements"""
        # Background
        self.screen.fill((50, 50, 50))
        
        # Update visualizer state before drawing
        self.viz.start = self.maze_state.start
        self.viz.goal = self.maze_state.end
        self.viz.end = self.maze_state.end  # Add this line - visualizer uses 'end' not 'goal'
        self.viz.maze = self.maze_state.maze
        self.viz.draw_grid(self.screen, path=self.maze_state.shortest_path)
        
        # UI panel background
        pygame.draw.rect(self.screen, (30, 30, 30), (580, 30, 190, 450))
        
        # Find Path button
        pygame.draw.rect(self.screen, (70, 130, 180), self.ui_state.find_button)
        self.screen.blit(
            self.font.render("Find Path", True, (255, 255, 255)),
            (self.ui_state.find_button.x + 30, self.ui_state.find_button.y + 10)
        )
        
        # Clear Maze button
        pygame.draw.rect(self.screen, (180, 70, 70), self.ui_state.clear_button)
        self.screen.blit(
            self.font.render("Clear Maze", True, (255, 255, 255)),
            (self.ui_state.clear_button.x + 20, self.ui_state.clear_button.y + 10)
        )
        
        # Algorithm section
        self.screen.blit(
            self.font.render("Algorithm:", True, (220, 220, 220)),
            (600, 145)
        )
        for rect, name in self.ui_state.algo_buttons:
            color = (100, 180, 100) if name == self.ui_state.selected_algo else (100, 100, 100)
            pygame.draw.rect(self.screen, color, rect)
            self.screen.blit(
                self.font.render(name, True, (255, 255, 255)),
                (rect.x + 10, rect.y + 7)
            )
        
        # Edit mode section
        self.screen.blit(
            self.font.render("Edit Mode:", True, (220, 220, 220)),
            (600, 285)
        )
        for rect, mode, label in self.ui_state.mode_buttons:
            color = (180, 100, 100) if mode == self.ui_state.edit_mode else (100, 100, 100)
            pygame.draw.rect(self.screen, color, rect)
            self.screen.blit(
                self.font.render(label, True, (255, 255, 255)),
                (rect.x + 10, rect.y + 7)
            )
        
        # Status section
        status_y = 430
        self.screen.blit(
            self.font.render(f"Algo: {self.ui_state.selected_algo}", True, (220, 220, 220)),
            (600, status_y)
        )
        self.screen.blit(
            self.font.render(f"Mode: {self.ui_state.edit_mode}", True, (220, 220, 220)),
            (600, status_y + 20)
        )
        
        # Start/End status
        start_text = f"Start: {self.maze_state.start if self.maze_state.start else 'Not set'}"
        end_text = f"End: {self.maze_state.end if self.maze_state.end else 'Not set'}"
        self.screen.blit(
            self.error_font.render(start_text, True, (180, 180, 180)),
            (600, status_y + 45)
        )
        self.screen.blit(
            self.error_font.render(end_text, True, (180, 180, 180)),
            (600, status_y + 60)
        )
        
        # Error message
        if self.ui_state.error_timer > 0:
            error_surf = self.error_font.render(
                self.ui_state.error_message, True, (255, 100, 100)
            )
            error_rect = error_surf.get_rect(center=(400, 550))
            bg_rect = error_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (40, 40, 40), bg_rect)
            pygame.draw.rect(self.screen, (255, 100, 100), bg_rect, 2)
            self.screen.blit(error_surf, error_rect)
    
    def run(self):
        """Main application loop"""
        while self.running:
            self.handle_events()
            self.ui_state.update_error_timer()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()


def main():
    app = SPFAVisualizer()
    app.run()


if __name__ == "__main__":
    main()