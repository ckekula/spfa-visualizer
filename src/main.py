import pygame
import threading
from maze import MazeVisualizer, MazeState, UIState
from algorithms import PathFinder

# CONFIG
ROWS = 10
COLS = 10
# Increase cell size for a larger visible grid and make window caps larger
CELL_SIZE = 50  # Small default cell size


class SPFAVisualizer:
    """Main application class"""
    def __init__(self):
        pygame.init()
        
        # Get display info and set window size
        display_info = pygame.display.Info()
        # Use smaller caps for a smaller display by default
        self.screen_width = min(1400, display_info.current_w - 100)
        self.screen_height = min(900, display_info.current_h - 100)
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("SPFA Visualizer - Interactive")
        self.clock = pygame.time.Clock()
        
        # Original font sizes
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 32)
        self.error_font = pygame.font.SysFont(None, 20)
        
        # Calculate grid position (centered)
        self.grid_width = COLS * CELL_SIZE
        self.grid_height = ROWS * CELL_SIZE
        # Place grid centered horizontally, but slightly higher vertically so
        # there is less empty gap below the title.
        center_x = (self.screen_width - self.grid_width) // 2
        center_y = (self.screen_height - self.grid_height) // 2

        # Title is drawn at y=30; keep a small margin between title and grid.
        # title_bottom = 30 + 10  # title center 30 plus margin
        # grid_origin_y = max(title_bottom + 10, center_y - 10)

        self.grid_origin = (center_x, 70)
        
        # Calculate panel positions
        self.left_panel_x = 40
        self.right_panel_x = self.screen_width - 280
        
        # Initialize state components
        self.maze_state = MazeState(ROWS, COLS)
        self.ui_state = UIState(self.left_panel_x, self.right_panel_x, self.screen_height)
        
        # Initialize visualizer
        self.viz = MazeVisualizer(
            rows=ROWS, cols=COLS, cell_size=CELL_SIZE,
            grid_origin=self.grid_origin, maze=self.maze_state.maze,
            start=None, end=None
        )
        
        # Initialize pathfinder
        self.pathfinder = PathFinder(self.viz, self.maze_state)
        
        # Speed control
        self.animation_speed = 0.05  # seconds between steps
        
        self.running = True
        self.computing_thread = None
    
    def handle_grid_click(self, mx, my):
        """Handle clicks on the maze grid"""
        # Don't allow editing while computing
        if self.pathfinder.is_computing:
            return
            
        gx = mx - self.grid_origin[0]
        gy = my - self.grid_origin[1]
        
        if gx < 0 or gy < 0:
            return
        
        col = gx // CELL_SIZE
        row = gy // CELL_SIZE
        
        if 0 <= row < ROWS and 0 <= col < COLS:
            if self.ui_state.edit_mode == "wall":
                self.maze_state.toggle_wall(row, col)
            elif self.ui_state.edit_mode == "start":
                self.maze_state.set_start(row, col)
            elif self.ui_state.edit_mode == "end":
                self.maze_state.set_end(row, col)
    
    def compute_path_async(self):
        """Run pathfinding in a separate thread"""
        try:
            self.pathfinder.compute_path(self.ui_state.selected_algo, delay=self.animation_speed)
        except ValueError as e:
            self.ui_state.show_error(f"Error: {str(e)}")
        except Exception as e:
            self.ui_state.show_error(f"Error: {str(e)}")
    
    def handle_button_clicks(self, mx, my):
        """Handle clicks on UI buttons"""
        # Find Path button
        if self.ui_state.find_button.collidepoint(mx, my):
            if not self.pathfinder.is_computing:
                # Start computation in a separate thread
                self.computing_thread = threading.Thread(target=self.compute_path_async)
                self.computing_thread.start()
            return True
        
        # Don't allow other actions while computing
        if self.pathfinder.is_computing:
            return True
        
        # Clear Maze button
        if self.ui_state.clear_button.collidepoint(mx, my):
            self.maze_state.clear()
            return True

        # Preset buttons
        for rect, preset_id, _ in self.ui_state.preset_buttons:
            if rect.collidepoint(mx, my):
                if not self.pathfinder.is_computing:
                    try:
                        self.maze_state.set_preset(preset_id)
                        self.ui_state.show_error(f"Loaded preset {preset_id}")
                    except Exception as e:
                        self.ui_state.show_error(f"Preset load failed: {e}")
                return True
        
        # Algorithm selection buttons
        for rect, name in self.ui_state.algo_buttons:
            if rect.collidepoint(mx, my):
                self.ui_state.selected_algo = name
                return True
        
        # Edit mode buttons
        for rect, mode, _ in self.ui_state.mode_buttons:
            if rect.collidepoint(mx, my):
                self.ui_state.edit_mode = mode
                return True
        
        # Speed control buttons
        for rect, speed_val, _ in self.ui_state.speed_buttons:
            if rect.collidepoint(mx, my):
                self.animation_speed = speed_val
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
                    self.grid_origin[0], self.grid_origin[1],
                    self.grid_width, self.grid_height
                )
                if grid_rect.collidepoint(mx, my):
                    self.handle_grid_click(mx, my)
                else:
                    self.handle_button_clicks(mx, my)
    
    def draw_ui(self):
        """Draw all UI elements"""
        # Background with gradient effect
        self.screen.fill((45, 45, 55))
        
        # Draw title
        title_text = "SPFA Pathfinding Visualizer"
        if self.pathfinder.is_computing:
            title_text += " - Computing..."
        title_surf = self.title_font.render(title_text, True, (220, 220, 240))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 30))
        self.screen.blit(title_surf, title_rect)
        
        # Update visualizer state before drawing
        self.viz.start = self.maze_state.start
        self.viz.goal = self.maze_state.end
        self.viz.end = self.maze_state.end
        self.viz.maze = self.maze_state.maze
        self.viz.draw_grid(self.screen, path=self.maze_state.shortest_path, intermediate_steps=self.maze_state.intermediate_steps)

        # --- Comparative bars for all algorithms (below the grid) ---
        # Keep only the comparative bars for all algorithms; the single selected
        # algorithm timing strip above the bars has been removed per request.
        grid_mid_x = self.grid_origin[0] + self.grid_width // 2
        time_y = self.grid_origin[1] + self.grid_height + 16
        padding_h = 22
        padding_v = 10

        # --- Comparative bars for all algorithms (below the single-line info) ---
        # Gather measurement data
        alg_entries = []
        for _, name in self.ui_state.algo_buttons:
            rec = self.maze_state.timings.get(name)
            alg_entries.append((name, rec))

        if alg_entries:
            # Determine available timings, ignore None values to compute min/max
            measured = [e[1]["time"] for e in alg_entries if e[1] is not None]
            measured_ms = [t * 1000 for t in measured]

            # Sort algorithms: measured by time ascending, then unmeasured
            def _sort_key(entry):
                rec = entry[1]
                return rec["time"] if rec else float('inf')

            alg_entries.sort(key=_sort_key)

            # Setup layout under the center bar
            bar_top = time_y + padding_v + 22
            bar_height = 18
            full_bar_width = min(self.grid_width - 40, 600)  # clamp width
            bar_left = grid_mid_x - full_bar_width // 2

            # Compute scale: bigger bars should be slower times. We'll scale relative to max.
            if measured_ms:
                max_ms = max(measured_ms)
                min_ms = min(measured_ms)
                # Avoid division by zero
                range_ms = max_ms - min_ms if max_ms - min_ms > 1e-9 else max_ms
            else:
                max_ms = min_ms = range_ms = 0

            for i, (name, rec) in enumerate(alg_entries):
                y = bar_top + i * (bar_height + 8)

                is_sel = name == self.ui_state.selected_algo
                if is_sel:
                    # Draw a subtle highlight behind selected algorithm's track
                    sel_rect = pygame.Rect(bar_left - 6, y - 6, full_bar_width + 12, bar_height + 12)
                    pygame.draw.rect(self.screen, (30, 50, 42), sel_rect, border_radius=8)

                # Draw label
                lbl_color = (220, 220, 240) if rec else (140, 140, 150)
                name_text = self.error_font.render(name, True, lbl_color)
                self.screen.blit(name_text, (bar_left - 120, y + 1))

                # Draw background track
                track_rect = pygame.Rect(bar_left, y, full_bar_width, bar_height)
                pygame.draw.rect(self.screen, (40, 40, 46), track_rect, border_radius=6)

                if rec is None:
                    # Unmeasured state: render small dash and a label
                    dash_rect = pygame.Rect(bar_left + 4, y + 2, 10, bar_height - 4)
                    pygame.draw.rect(self.screen, (80, 80, 90), dash_rect, border_radius=4)
                    na_text = self.error_font.render("N/A", True, (120, 130, 140))
                    self.screen.blit(na_text, (bar_left + full_bar_width + 8, y))
                else:
                    ms = rec.get("time", 0) * 1000
                    # Normalize: map ms to width relative to max_ms
                    if max_ms <= 0:
                        frac = 0
                    else:
                        # Map to [0.1, 1.0] to always show minimal width for fastest
                        frac = max(0.05, ms / max_ms)

                    fill_w = int(full_bar_width * frac)
                    fill_rect = pygame.Rect(bar_left, y, fill_w, bar_height)

                    # Color scale: fast (green) -> slow (orange) -> slowest (red)
                    # Use frac as speed indicator (higher frac = slower)
                    if frac < 0.4:
                        col = (100, 200, 120)
                    elif frac < 0.75:
                        col = (255, 170, 80)
                    else:
                        col = (240, 100, 100)

                    pygame.draw.rect(self.screen, col, fill_rect, border_radius=6)

                    # Draw right-time label
                    time_label = f"{ms:.2f} ms" if ms < 1000 else f"{ms/1000:.2f} s"
                    nodes_label = f" {rec.get('visited', 0)} nodes"
                    label_text = self.error_font.render(time_label + nodes_label, True, (180, 210, 200))
                    label_rect = label_text.get_rect()
                    if is_sel:
                        # Selected algorithm label draws slightly brighter
                        label_text = self.error_font.render(time_label + nodes_label, True, (220, 240, 220))
                    self.screen.blit(label_text, (bar_left + full_bar_width + 8, y))
        
        # LEFT PANEL - Edit Controls
        self.draw_left_panel()
        
        # RIGHT PANEL - Algorithm Selection
        self.draw_right_panel()
        
        # Error message at bottom
        if self.ui_state.error_timer > 0:
            error_surf = self.error_font.render(
                self.ui_state.error_message, True, (255, 120, 120)
            )
            error_rect = error_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
            bg_rect = error_rect.inflate(30, 15)
            pygame.draw.rect(self.screen, (60, 40, 40), bg_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 100, 100), bg_rect, 2, border_radius=8)
            self.screen.blit(error_surf, error_rect)
    
    def draw_left_panel(self):
        """Draw left control panel"""
        panel_x = self.left_panel_x
        panel_y = 80
        panel_width = 240
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, self.screen_height - 160)
        pygame.draw.rect(self.screen, (35, 35, 45), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 80, 100), panel_rect, 2, border_radius=10)
        
        # Section title
        y_offset = panel_y + 20
        title = self.font.render("Edit Controls", True, (220, 220, 240))
        self.screen.blit(title, (panel_x + 70, y_offset))
        
        y_offset += 50
        
        # Edit mode buttons
        for rect, mode, label in self.ui_state.mode_buttons:
            is_selected = mode == self.ui_state.edit_mode
            is_disabled = self.pathfinder.is_computing
            
            if is_disabled:
                color = (50, 50, 60)
                border_color = (70, 70, 80)
            else:
                color = (100, 150, 220) if is_selected else (70, 70, 85)
                border_color = (150, 180, 240) if is_selected else (100, 100, 120)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)
            
            text_color = (150, 150, 150) if is_disabled else (255, 255, 255)
            text = self.font.render(label, True, text_color)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # Find Path button
        is_computing = self.pathfinder.is_computing
        button_color = (50, 100, 140) if is_computing else (70, 140, 200)
        border_color = (70, 120, 160) if is_computing else (100, 170, 230)
        button_text = "Computing..." if is_computing else "Find Path"

        pygame.draw.rect(self.screen, button_color, self.ui_state.find_button, border_radius=8)
        pygame.draw.rect(self.screen, border_color, self.ui_state.find_button, 3, border_radius=8)
        find_text = self.font.render(button_text, True, (255, 255, 255))
        find_rect = find_text.get_rect(center=self.ui_state.find_button.center)
        self.screen.blit(find_text, find_rect)
        
        # Clear button
        is_disabled = self.pathfinder.is_computing
        clear_color = (100, 40, 40) if is_disabled else (180, 70, 70)
        clear_border = (120, 60, 60) if is_disabled else (220, 100, 100)
        
        pygame.draw.rect(self.screen, clear_color, self.ui_state.clear_button, border_radius=8)
        pygame.draw.rect(self.screen, clear_border, self.ui_state.clear_button, 2, border_radius=8)
        
        text_color = (150, 150, 150) if is_disabled else (255, 255, 255)
        clear_text = self.font.render("Clear Maze", True, text_color)
        clear_rect = clear_text.get_rect(center=self.ui_state.clear_button.center)
        self.screen.blit(clear_text, clear_rect)

        # Preset buttons (below Clear)
        for rect, pid, label in self.ui_state.preset_buttons:
            is_disabled = self.pathfinder.is_computing
            color = (70, 70, 85) if is_disabled else (120, 100, 200)
            border_color = (100, 100, 120) if is_disabled else (170, 150, 240)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)
            ptext = self.font.render(label, True, (255, 255, 255) if not is_disabled else (150, 150, 150))
            p_rect = ptext.get_rect(center=rect.center)
            self.screen.blit(ptext, p_rect)
        
        # Speed control section
        # Speed control sits below the preset buttons (computed inside UIState)
        speed_y = self.ui_state.preset_buttons[-1][0].bottom + 20
        speed_title = self.font.render("Animation Speed", True, (220, 220, 240))
        self.screen.blit(speed_title, (panel_x + 50, speed_y))
        
        for rect, speed_val, label in self.ui_state.speed_buttons:
            is_selected = abs(self.animation_speed - speed_val) < 0.001
            color = (100, 150, 220) if is_selected else (70, 70, 85)
            border_color = (150, 180, 240) if is_selected else (100, 100, 120)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)
            
            text = self.error_font.render(label, True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Status info
        status_y = self.ui_state.speed_buttons[-1][0].bottom + 10
        
        status_lines = [
            f"Current Mode - {self.ui_state.edit_mode.title()}",
            f"Start Position - {self.maze_state.start if self.maze_state.start else 'Not set'}",
            f"End Position - {self.maze_state.end if self.maze_state.end else 'Not set'}",
        ]
        
        for i, line in enumerate(status_lines):
            color = (200, 200, 220) if line and not line.startswith("  ") else (160, 160, 180)
            text = self.error_font.render(line, True, color)
            self.screen.blit(text, (panel_x + 20, status_y + i * 22))
    
    def draw_right_panel(self):
        """Draw right algorithm panel"""
        panel_x = self.right_panel_x
        panel_y = 80
        panel_width = 240
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, self.screen_height - 160)
        pygame.draw.rect(self.screen, (35, 35, 45), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 80, 100), panel_rect, 2, border_radius=10)
        
        # Section title
        y_offset = panel_y + 20
        title = self.font.render("Algorithm", True, (220, 220, 240))
        self.screen.blit(title, (panel_x + 75, y_offset))

        y_offset += 50

        # Algorithm buttons
        for rect, name in self.ui_state.algo_buttons:
            is_selected = name == self.ui_state.selected_algo
            is_disabled = self.pathfinder.is_computing

            if is_disabled:
                color = (50, 60, 50)
                border_color = (70, 80, 70)
            else:
                color = (100, 180, 120) if is_selected else (70, 70, 85)
                border_color = (130, 220, 150) if is_selected else (100, 100, 120)

            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)

            text_color = (150, 150, 150) if is_disabled else (255, 255, 255)
            text = self.font.render(name, True, text_color)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
    
        # Find Path button
        is_computing = self.pathfinder.is_computing
        button_color = (50, 100, 140) if is_computing else (70, 140, 200)
        border_color = (70, 120, 160) if is_computing else (100, 170, 230)
        button_text = "Computing..." if is_computing else "Find Path"

        pygame.draw.rect(self.screen, button_color, self.ui_state.find_button, border_radius=8)
        pygame.draw.rect(self.screen, border_color, self.ui_state.find_button, 3, border_radius=8)
        find_text = self.font.render(button_text, True, (255, 255, 255))
        find_rect = find_text.get_rect(center=self.ui_state.find_button.center)
        self.screen.blit(find_text, find_rect)

        # Selected algorithm info
        info_y = self.ui_state.find_button.bottom + 40
        info_lines = [
            "Selected Algorithm:",
            f"  {self.ui_state.selected_algo}",
        ]

        for i, line in enumerate(info_lines):
            color = (200, 200, 220) if not line.startswith("  ") else (160, 220, 160)
            text = self.error_font.render(line, True, color)
            self.screen.blit(text, (panel_x + 20, info_y + i * 22))

    def run(self):
        """Main application loop"""
        while self.running:
            self.handle_events()
            self.ui_state.update_error_timer()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
        
        # Wait for computation thread to finish before closing
        if self.computing_thread and self.computing_thread.is_alive():
            self.pathfinder.is_computing = False
            self.computing_thread.join(timeout=1.0)
        
        pygame.quit()


def main():
    app = SPFAVisualizer()
    app.run()


if __name__ == "__main__":
    main()