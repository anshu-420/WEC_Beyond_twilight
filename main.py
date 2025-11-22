import pygame
from layers import getObjects

# --- Settings ---
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 200, 200
SUB_SIZE = 4
CELL_SIZE = WIDTH // COLS

LAYERS = 6
TOP_RADIUS = 75
MIN_RADIUS = 20

# Colors
BLACK      = (0, 0, 0)
BASE_COLOR = (15, 50, 155)
ACTIVE     = (255, 255, 255)
SELECTED   = (0, 255, 0)   # chosen pixel highlight (green)
OBJ_COLOR  = (255, 0, 0)
GRID_LINE  = (70, 70, 70)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# logical grid (0 = off, 1 = active)
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# viewport and selection state
viewport_center = None          # (col,row) or None
selected = None                 # (col,row) user-selected pixel (must be inside viewport)
current_layer = 1
objects_in_layer = getObjects(current_layer)

def radius_for_layer(layer):
    """Linear interpolation from TOP_RADIUS (layer=1) to MIN_RADIUS (layer=LAYERS)."""
    if LAYERS <= 1:
        return MIN_RADIUS
    t = (layer - 1) / (LAYERS - 1)
    return int(round(TOP_RADIUS * (1 - t) + MIN_RADIUS * t))

def pixel_to_cell(mx, my):
    return mx // CELL_SIZE, my // CELL_SIZE

def in_viewport(col, row, center, radius):
    """Square viewport check: Chebyshev distance <= radius."""
    if center is None:
        return True
    ccol, crow = center
    return abs(col - ccol) <= radius and abs(row - crow) <= radius

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # depth control: DOWN to go deeper, UP to go shallower
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN and current_layer < LAYERS:
                # going deeper: the selected pixel (must be inside current viewport) becomes the new viewport center
                if selected is not None:
                    viewport_center = selected
                current_layer += 1
                objects_in_layer = getObjects(current_layer)
                # when deeper, radius_for_layer will shrink automatically during draw
            elif event.key == pygame.K_UP and current_layer > 1:
                # going shallower: keep the same viewport center but increase radius
                current_layer -= 1
                objects_in_layer = getObjects(current_layer)

        # mouse click: select pixel only if it's inside the current viewport (non-black)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            col, row = pixel_to_cell(mx, my)
            if not (0 <= col < COLS and 0 <= row < ROWS):
                continue

            layer_radius = radius_for_layer(current_layer)
            # if no viewport_center yet (first click), allow click anywhere and set viewport_center
            if viewport_center is None:
                viewport_center = (col, row)
                selected = (col, row)
                # set active cell (cursor-like), clear others
                for r in range(ROWS):
                    for c in range(COLS):
                        grid[r][c] = 0
                grid[row][col] = 1
                objects_in_layer = getObjects(current_layer)
            else:
                # only allow clicks inside the currently visible bounds (non-black)
                if in_viewport(col, row, viewport_center, layer_radius):
                    selected = (col, row)   # store selection, but do NOT change viewport bounds now
                    # optionally set active cell
                    for r in range(ROWS):
                        for c in range(COLS):
                            grid[r][c] = 0
                    grid[row][col] = 1
                    # we do NOT call getObjects or change radius here; that happens on DOWN key
                else:
                    print("Click ignored: outside visible (black) area.")

    # Drawing
    screen.fill(BLACK)
    layer_radius = radius_for_layer(current_layer)

    if viewport_center is None:
        cmin, cmax = 0, COLS - 1
        rmin, rmax = 0, ROWS - 1
    else:
        vc_col, vc_row = viewport_center
        cmin = max(0, vc_col - layer_radius)
        cmax = min(COLS - 1, vc_col + layer_radius)
        rmin = max(0, vc_row - layer_radius)
        rmax = min(ROWS - 1, vc_row + layer_radius)

    # fill visible area with BASE_COLOR
    for r in range(rmin, rmax + 1):
        for c in range(cmin, cmax + 1):
            pygame.draw.rect(screen, BASE_COLOR, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # draw objects for current layer (if provided by getObjects)
    try:
        if objects_in_layer:
            # scale factor from source (50x50) to current grid (e.g. 200x200 => scale=4)
            src_size = 50
            scale = max(1, COLS // src_size)

            for df in objects_in_layer.values():
                for _, rowobj in df.iterrows():
                    if 'col' in rowobj and 'row' in rowobj:
                        # source coords in 50x50 space
                        src_c = int(rowobj['col'])
                        src_r = int(rowobj['row'])

                        # scale up to 200x200 grid coords
                        oc = src_c * scale
                        orow = src_r * scale

                        # object's extent in scaled coordinates (inclusive start, exclusive end)
                        oc_end = oc + scale  # exclusive
                        orow_end = orow + scale

                        # skip objects fully outside viewport (fast rejection)
                        if oc_end <= cmin or oc >= cmax + 1 or orow_end <= rmin or orow >= rmax + 1:
                            continue

                        # draw scaled object as a block of size (scale x scale) logical cells
                        x_px = oc * CELL_SIZE
                        y_px = orow * CELL_SIZE
                        w_px = scale * CELL_SIZE
                        h_px = scale * CELL_SIZE
                        pygame.draw.rect(screen, OBJ_COLOR, (x_px, y_px, w_px, h_px))
    except Exception:
        pass

    # draw active cell(s) on top
    for r in range(rmin, rmax + 1):
        for c in range(cmin, cmax + 1):
            if grid[r][c] == 1:
                pygame.draw.rect(screen, ACTIVE, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # draw selection marker (if any) inside viewport
    if selected is not None:
        sc, sr = selected
        if cmin <= sc <= cmax and rmin <= sr <= rmax:
            pygame.draw.rect(screen, SELECTED, (sc * CELL_SIZE, sr * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

    # grid lines limited to viewport area
    for c in range(cmin, cmax + 1, SUB_SIZE):
        x = c * CELL_SIZE
        pygame.draw.line(screen, GRID_LINE, (x, rmin * CELL_SIZE), (x, (rmax + 1) * CELL_SIZE), 1)
    for r in range(rmin, rmax + 1, SUB_SIZE):
        y = r * CELL_SIZE
        pygame.draw.line(screen, GRID_LINE, (cmin * CELL_SIZE, y), ((cmax + 1) * CELL_SIZE, y), 1)

    pygame.display.set_caption(f"Layer {current_layer}/{LAYERS}  radius={layer_radius}")
    pygame.display.flip()
    clock.tick(60)

pygame.quit()