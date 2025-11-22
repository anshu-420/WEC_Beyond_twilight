#Team Name: Anything Works

import numpy as np
from typing import Tuple

# Compute viewport bounds given center and radius
def compute_viewport_bounds(center_col, center_row, view_radius, grid_w, grid_h):
    col_min = max(0, center_col - view_radius)
    col_max = min(grid_w - 1, center_col + view_radius)
    row_min = max(0, center_row - view_radius)
    row_max = min(grid_h - 1, center_row + view_radius)
    return col_min, col_max, row_min, row_max

# Compute a boolean mask of visible cells within the viewport
def visible_mask(center_col, center_row, radius, grid_w, grid_h):
    cols = np.arange(grid_w)[None, :]        
    rows = np.arange(grid_h)[:, None]

    # boolean viewOrNot where cells are within the square viewport or not
    viewOrNot = (np.abs(cols - center_col) <= radius) & (np.abs(rows - center_row) <= radius)
    return viewOrNot

# Apply viewport mask to RGB grid and the outside color set to black
def apply_viewport_to_rgb(rgb_grid, mask, outside_color=(0,0,0)):
    out = np.zeros_like(rgb_grid, dtype=np.uint8)
    out[mask] = rgb_grid[mask]      # set inside cells to original colors
    out[~mask] = outside_color      # set outside cells to black
    return out

def upscale_grid_to_image(rgb_grid, cell_px=2):
    # if cell_px <= 1, return original
    if cell_px <= 1:
        return rgb_grid.copy()
    # else upscale using np.kron to repeat each cell_px times in both dimensions
    return np.kron(rgb_grid, np.ones((cell_px, cell_px, 1), dtype=np.uint8))