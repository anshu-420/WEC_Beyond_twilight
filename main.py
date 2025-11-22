#Team Name: Anything Works

import pygame
from user_hud import HUD, OBJECT_COLORS 
from layers import getObjects

# --- Settings ---
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 900
GRID_WIDTH, GRID_HEIGHT = 800, 800 # area for grid (top)
ROWS, COLS = 200, 200
SUB_SIZE = 4
CELL_SIZE = WINDOW_WIDTH // COLS

LAYERS = 6
TOP_RADIUS = 75
MIN_RADIUS = 20

# Colors
BLACK      = (0, 0, 0)
BASE_COLOR = (15, 50, 155)
ACTIVE     = (255, 255, 255)
SELECTED   = (255, 255, 255)   # chosen pixel highlight (green)
GRID_LINE  = (70, 70, 70)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# logical grid (0 = off, 1 = active)
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

hud = HUD(grid_height=GRID_HEIGHT, window_width=WINDOW_WIDTH)

# Initial values
current_layer = 1
hud.hull_health = 100
hud.fuel = 100
hud.depth_m = current_layer * 100   # NEW: depth based on layer (1 -> 100m)

# viewport and selection state
viewport_center = None          # (col,row) or None
selected = None                 # (col,row) user-selected pixel (must be inside viewport)
prev_selected = None
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
                hud.depth_m = current_layer * 100          # NEW: update depth
                objects_in_layer = getObjects(current_layer)
                # when deeper, radius_for_layer will shrink automatically during draw
            elif event.key == pygame.K_UP and current_layer > 1:
                # going shallower: keep the same viewport center but increase radius
                current_layer -= 1
                hud.depth_m = current_layer * 100          # NEW: update depth
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
                if prev_selected is not None:
                    dx = selected[0] - prev_selected[0]
                    dy = selected[1] - prev_selected[1]
                    dist = (dx*dx + dy*dy) ** 0.5     # sqrt(a^2 + b^2)
                    hud.fuel = max(0, hud.fuel - 0.1 * dist)

                prev_selected = selected

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

                # iterate with the object type key so we know what color to use
                for obj_type, df in objects_in_layer.items():
                    color = OBJECT_COLORS.get(obj_type, (255, 0, 0))  # fallback red if missing

                    for _, rowobj in df.iterrows():
                        if 'col' in rowobj and 'row' in rowobj:
                            # source coords in 50x50 space
                            src_c = int(rowobj['col'])
                            src_r = int(rowobj['row'])

                            # scale up to 200x200 grid coords
                            oc = src_c * scale
                            orow = src_r * scale

                            oc_end = oc + scale
                            orow_end = orow + scale

                            # skip objects fully outside viewport
                            if oc_end <= cmin or oc >= cmax + 1 or orow_end <= rmin or orow >= rmax + 1:
                                continue

                            x_px = oc * CELL_SIZE
                            y_px = orow * CELL_SIZE
                            w_px = scale * CELL_SIZE
                            h_px = scale * CELL_SIZE

                            pygame.draw.rect(screen, color, (x_px, y_px, w_px, h_px))
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

    # draw HUD
    hud.draw(screen)

    pygame.display.set_caption(f"Layer {current_layer}/{LAYERS}  radius={layer_radius}")
    pygame.display.flip()
    clock.tick(60)

    if hud.fuel <= 0:
        pygame.quit()
        running = False

pygame.quit()
