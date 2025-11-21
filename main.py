import pygame
import sys

# --- Settings ---
WIDTH, HEIGHT = 800, 800
FPS = 60
WINDOW_TITLE = "50 x 50 Clickable Grid"

ROWS, COLS = 50, 50
CELL_SIZE = WIDTH // COLS  # square window

# Colors
BLACK = (0, 0, 0)
ACTIVE = (255, 255, 255)


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = True

        # 2D grid: 0 = off, 1 = on
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

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

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    mx, my = event.pos
                    col = mx // CELL_SIZE
                    row = my // CELL_SIZE

                    if 0 <= row < ROWS and 0 <= col < COLS:
                        # clear entire grid
                        for r in range(ROWS):
                            for c in range(COLS):
                                self.grid[r][c] = 0

                        # set ONLY the current cell to active
                        self.grid[row][col] = 1

    def update(self):
        # no movement logic needed for now
        pass

    def draw(self):
        self.screen.fill(BLACK)

        for row in range(ROWS):
            for col in range(COLS):
                x = col * CELL_SIZE
                y = row * CELL_SIZE

                if self.grid[row][col] == 1:
                    color = ACTIVE
                else:
                    color = BLACK

                # filled cell
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                # optional grid line
                pygame.draw.rect(self.screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)

        pygame.display.flip()


def main():
    game = Game()
    while game.running:
        game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
