import pygame
import sys

# --- Settings ---
WIDTH, HEIGHT = 800, 800
FPS = 60
WINDOW_TITLE = "Beyond Twilight"

# Colors
BLACK = (0, 0, 0)
GRID_Lines = (40, 40, 40)
ACTIVE_AREA = (50, 150, 255)

# Seting up grind dimensions
ROW, COL = 50, 50
CELL_AREA = WIDTH / COL

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = True  # only used if you add menus later

    def run(self):
        while self.playing:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                    self.running = False

    def update(self):
        """Game logic goes here."""
        pass

    def draw(self):
        """Drawing goes here."""
        self.screen.fill(BLACK)
        pygame.display.flip()

def main():
    game = Game()
    while game.running:
        game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
