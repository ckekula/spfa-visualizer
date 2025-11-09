import pygame

def main():
    # Initialize Pygame
    pygame.init()

    # Set up display
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("SPFA Visualizer")

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen with a color
        screen.fill((0, 128, 255))

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    main()