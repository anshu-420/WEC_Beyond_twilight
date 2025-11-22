#Team Name: Anything Works

import pygame
from user_hud import HUD, OBJECT_COLORS, OBJECT_LABELS
from layers import getObjects
import pandas as pd

# all the objects types we have in dataset
OBJ_TYPES = ['corals', 'food_web', 'hazards', 'life', 'poi', 'resources']

# function to build objects store
def build_objects_store(getObjects_func, layers: int, cols: int, src_size: int = 50):
    scale = max(1, cols // src_size)
    store = {}      

    # Iterate over each layer to build the store
    for layer in range(1, layers + 1):
        raw = getObjects_func(layer)
        layer_store = {}

        # If no objects in this layer, initialize empty lists for each object type
        if not raw:
            for ot in OBJ_TYPES:
                layer_store[ot] = []
            store[layer] = layer_store
            continue

        # Process each object type in this layer
        for objectType in OBJ_TYPES:
            df = raw.get(objectType)
            objects = []
            if df is None:
                layer_store[objectType] = objects
                continue

            # Scale and store each object
            for _, r in df.iterrows():
                if 'col' not in r or 'row' not in r:
                    continue
                try:
                    src_col = int(r['col'])
                    src_row = int(r['row'])
                except Exception:
                    continue

                scaled_col = src_col * scale
                scaled_row = src_row * scale
                w_src = int(r['width']) if 'width' in r and not pd.isna(r['width']) else 1
                h_src = int(r['height']) if 'height' in r and not pd.isna(r['height']) else 1
                scaled_w = max(1, w_src * scale)
                scaled_h = max(1, h_src * scale)

                obj = {
                    'type': objectType,
                    'src_col': src_col,
                    'src_row': src_row,
                    'col': int(scaled_col),
                    'row': int(scaled_row),
                    'w': int(scaled_w),
                    'h': int(scaled_h),
                    'meta': r.to_dict(),
                }
                objects.append(obj)

            layer_store[objectType] = objects
        store[layer] = layer_store
    return store

# function to collect object at (col,row) in given layer
def collect_at(objects_store, col, row, layer):
    layer_objs = objects_store.get(layer)
    if not layer_objs:
        return None
    for obj_type, obj_list in layer_objs.items():
        i = 0
        while i < len(obj_list):
            obj = obj_list[i]
            oc = int(obj['col'])
            orow = int(obj['row'])
            w = int(obj.get('w', 1))
            h = int(obj.get('h', 1))
            if oc <= col < oc + w and orow <= row < orow + h:
                collected = obj_list.pop(i)
                return collected
            else:
                i += 1
    return None

# function to draw objects in current layer
def draw_objects(screen, objects_store, layer, cmin, cmax, rmin, rmax, cell_size, object_colors):
    layer_objs = objects_store.get(layer, {})
    for obj_type, obj_list in layer_objs.items():
        color = object_colors.get(obj_type, (255, 0, 0))

        # draw each object as rectangle
        for obj in obj_list:
            oc = int(obj['col'])
            orow = int(obj['row'])
            w = int(obj.get('w', 1))
            h = int(obj.get('h', 1))
            if oc + w - 1 < cmin or oc > cmax or orow + h - 1 < rmin or orow > rmax:
                continue
            x_px = oc * cell_size
            y_px = orow * cell_size
            w_px = w * cell_size
            h_px = h * cell_size
            pygame.draw.rect(screen, color, (x_px, y_px, w_px, h_px))


# define constants
Window_width, Window_height = 800, 900
GRID_WIDTH, GRID_HEIGHT = 800, 800 
ROWS, COLS = 200, 200
SUB_SIZE = 4
CELL_SIZE = Window_width // COLS

LAYERS = 6
TOP_RADIUS = 75
MIN_RADIUS = 20

# Colors
BLACK      = (0, 0, 0)
BASE_COLOR = (15, 50, 155)
ACTIVE     = (255, 255, 255)
SELECTED   = (255, 255, 255)
GRID_LINE  = (70, 70, 70)

pygame.init()
screen = pygame.display.set_mode((Window_width, Window_height))
clock = pygame.time.Clock()

# logical grid (0 = off, 1 = active)
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

hud = HUD(grid_height=GRID_HEIGHT, window_width=Window_width)

# Initial values
current_layer = 1
hud.hull_health = 100
hud.fuel = 100
hud.depth_m = current_layer * 100   # NEW: depth based on layer (1 -> 100m)

# viewport and selection state
viewport_center = None          # (col,row) or None
selected = None                 # (col,row) user-selected pixel (must be inside viewport)
prev_selected = None
# build objects store once (scale source 50x50 coords into our grid)
objects_store = build_objects_store(getObjects, layers=LAYERS, cols=COLS, src_size=50)
objects_in_layer = objects_store.get(current_layer, {})

# HUD maintains collected_counts and fonts; no local collected_counts required

# function to compute radius for a given layer
def radius_for_layer(layer):
    if LAYERS <= 1:
        return MIN_RADIUS
    t = (layer - 1) / (LAYERS - 1)
    return int(round(TOP_RADIUS * (1 - t) + MIN_RADIUS * t))

def pixel_to_cell(mx, my):
    return mx // CELL_SIZE, my // CELL_SIZE

# function to check if (col,row) is inside viewport
def in_viewport(col, row, center, radius):
    """Square viewport check: Chebyshev distance <= radius."""
    if center is None:
        return True
    ccol, crow = center
    return abs(col - ccol) <= radius and abs(row - crow) <= radius

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
        #DOWN to go deeper, UP to go up
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN and current_layer < LAYERS:
                if selected is not None:
                    viewport_center = selected
                current_layer += 1
                hud.depth_m = current_layer * 100  
                
                # switch to objects stored for new layer
                objects_in_layer = objects_store.get(current_layer, {})

            elif event.key == pygame.K_UP and current_layer > 1:
                # going up and keep the same viewport center but increase radius
                current_layer -= 1
                hud.depth_m = current_layer * 100
                objects_in_layer = objects_store.get(current_layer, {})

        # if user clicks mouse
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            col, row = pixel_to_cell(mx, my)
            if not (0 <= col < COLS and 0 <= row < ROWS):
                continue

            layer_radius = radius_for_layer(current_layer)      # update radius for current layer
            

            if viewport_center is None:
                viewport_center = (col, row)
                selected = (col, row)
                # set active cell (cursor-like), clear others
                for r in range(ROWS):
                    for c in range(COLS):
                        grid[r][c] = 0
                grid[row][col] = 1
                objects_in_layer = objects_store.get(current_layer, {})
            else:
                # only allow clicks inside the currently visible bounds (non-black)
                if in_viewport(col, row, viewport_center, layer_radius):
                    selected = (col, row)   # store selection, but do NOT change viewport bounds now
                    # optionally set active cell
                    for r in range(ROWS):
                        for c in range(COLS):
                            grid[r][c] = 0
                    grid[row][col] = 1

                    # try to collect any object at this selected cell in current layer
                    collected = collect_at(objects_store, col, row, current_layer)
                    if collected:
                        print("Collected:", collected['type'])
                        # update HUD counts
                        hud.increment_collected(collected['type'])
                
                # update fuel based on movement distance
                if prev_selected is not None:
                    dx = selected[0] - prev_selected[0]
                    dy = selected[1] - prev_selected[1]
                    dist = (dx*dx + dy*dy) ** 0.5     # sqrt(a^2 + b^2)
                    hud.fuel = max(0, hud.fuel - 0.1 * dist)

                prev_selected = selected

    screen.fill(BLACK)
    layer_radius = radius_for_layer(current_layer)      # update radius for current layer

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

        # draw objects for current layer from the in-memory store
        try:
            draw_objects(screen, objects_store, current_layer, cmin, cmax, rmin, rmax, CELL_SIZE, OBJECT_COLORS)
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
