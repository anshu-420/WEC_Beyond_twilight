import pygame

# --- Settings ---
WIDTH, HEIGHT = 800, 800          # square window
ROWS, COLS = 200, 200             # logical tiny cells
SUB_SIZE = 4                      # 4x4 tiny cells per "big" cell (for lines only)
CELL_SIZE = WIDTH // COLS         # 800 / 200 = 4 pixels per tiny cell
VIEW_RADIUS = 50                 # cells visible in each direction from center

# Colors
BLACK     = (0, 0, 0)
BASE_COLOR = (15, 50, 155)        # base blue for visible cells
ACTIVE    = (255, 255, 255)       # fill color for active tiny cells
GRID_LINE = (70, 70, 70)          # visible 50x50-style grid lines

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("200x200 Grid (fills like 200x200)")

# Full 200x200 logical grid: 0 = off, 1 = on
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Viewport center (None = no special viewport; will be set on click)
center_col = None
center_row = None

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

                # set viewport center to the clicked cell so we show nearby cells
                center_col = col
                center_row = row

                # If you instead want to toggle cells and keep previous ones,
                # comment out the clear loop above and use this line only:
                # grid[row][col] = 1 - grid[row][col]

    # --- Draw ---
    screen.fill(BLACK)

    # Determine viewport bounds (clamped)
    if center_col is None or center_row is None:
        cmin, cmax = 0, COLS - 1
        rmin, rmax = 0, ROWS - 1
    else:
        cmin = max(0, center_col - VIEW_RADIUS)
        cmax = min(COLS - 1, center_col + VIEW_RADIUS)
        rmin = max(0, center_row - VIEW_RADIUS)
        rmax = min(ROWS - 1, center_row + VIEW_RADIUS)

    # Fill the visible viewport area with base color, then draw active cells on top.
    for row in range(rmin, rmax + 1):
        for col in range(cmin, cmax + 1):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            # draw base visible cell background
            pygame.draw.rect(screen, BASE_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
            # draw active cell on top if set
            if grid[row][col] == 1:
                pygame.draw.rect(screen, ACTIVE, (x, y, CELL_SIZE, CELL_SIZE))

    # Draw "big" grid lines every SUB_SIZE tiny cells, but only inside viewport
    # vertical lines
    for c in range(cmin, cmax + 1, SUB_SIZE):
        x = c * CELL_SIZE
        pygame.draw.line(screen, GRID_LINE, (x, rmin * CELL_SIZE), (x, (rmax + 1) * CELL_SIZE), 1)

    # horizontal lines
    for r in range(rmin, rmax + 1, SUB_SIZE):
        y = r * CELL_SIZE
        pygame.draw.line(screen, GRID_LINE, (cmin * CELL_SIZE, y), ((cmax + 1) * CELL_SIZE, y), 1)

    pygame.display.update()

pygame.quit()
