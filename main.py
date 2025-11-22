import pygame

# --- Settings ---
WIDTH, HEIGHT = 800, 800          # square window
ROWS, COLS = 200, 200             # logical tiny cells
SUB_SIZE = 4                      # 4x4 tiny cells per "big" cell (for lines only)
CELL_SIZE = WIDTH // COLS         # 800 / 200 = 4 pixels per tiny cell

# Colors
BLACK     = (0, 0, 0)
ACTIVE    = (255, 255, 255)       # fill color for active tiny cells
GRID_LINE = (70, 70, 70)          # visible 50x50-style grid lines

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("200x200 Grid (fills like 200x200)")

# Full 200x200 logical grid: 0 = off, 1 = on
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

running = True
while running:

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if 0 <= mx < WIDTH and 0 <= my < HEIGHT:
                col = mx // CELL_SIZE      # 0..199
                row = my // CELL_SIZE      # 0..199

                # Option A: only current cell is active (like a cursor)
                # clear whole grid first
                for r in range(ROWS):
                    for c in range(COLS):
                        grid[r][c] = 0

                grid[row][col] = 1

                # If you instead want to toggle cells and keep previous ones,
                # comment out the clear loop above and use this line only:
                # grid[row][col] = 1 - grid[row][col]

    # --- Draw ---
    screen.fill(BLACK)

    # Fill ALL active tiny cells (true 200x200 logic)
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] == 1:
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                pygame.draw.rect(screen, ACTIVE, (x, y, CELL_SIZE, CELL_SIZE))

    # Draw ONLY "big" grid lines every 4 tiny cells so it *looks* 50x50
    # (you can remove this section to see the full 200x200)
    # vertical lines
    for c in range(0, COLS + 1, SUB_SIZE):
        x = c * CELL_SIZE
        pygame.draw.line(screen, GRID_LINE, (x, 0), (x, HEIGHT), 1)

    # horizontal lines
    for r in range(0, ROWS + 1, SUB_SIZE):
        y = r * CELL_SIZE
        pygame.draw.line(screen, GRID_LINE, (0, y), (WIDTH, y), 1)

    pygame.display.update()

pygame.quit()
