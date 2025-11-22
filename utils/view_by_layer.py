import numpy as np
import math
from typing import Tuple

def compute_viewport_bounds(center_col: int, center_row: int,
                            radius: int, grid_w: int, grid_h: int) -> Tuple[int,int,int,int]:
    """Return (col_min, col_max, row_min, row_max) clamped to grid."""
    col_min = max(0, center_col - radius)
    col_max = min(grid_w - 1, center_col + radius)
    row_min = max(0, center_row - radius)
    row_max = min(grid_h - 1, center_row + radius)
    return col_min, col_max, row_min, row_max

def visible_mask(center_col: int, center_row: int, radius: int,
                 grid_w: int, grid_h: int) -> np.ndarray:
    """Return boolean mask shape (grid_h, grid_w). True = visible."""
    # Create grid of indices (cols across axis1, rows across axis0)
    cols = np.arange(grid_w)[None, :]        # shape (1, grid_w)
    rows = np.arange(grid_h)[:, None]        # shape (grid_h, 1)
    mask = (np.abs(cols - center_col) <= radius) & (np.abs(rows - center_row) <= radius)
    return mask

def apply_viewport_to_rgb(rgb_grid: np.ndarray, mask: np.ndarray,
                          outside_color: Tuple[int,int,int]=(0,0,0)) -> np.ndarray:
    """
    rgb_grid: uint8 array shape (grid_h, grid_w, 3)
    mask: boolean array shape (grid_h, grid_w) where True means keep original colour
    outside_color: RGB tuple for masked-out cells (default black)
    Returns new uint8 image same shape as rgb_grid.
    """
    out = np.zeros_like(rgb_grid, dtype=np.uint8)
    out[mask] = rgb_grid[mask]
    out[~mask] = outside_color
    return out

def upscale_grid_to_image(rgb_grid: np.ndarray, cell_px: int=2) -> np.ndarray:
    """
    Upscale the grid to pixel image by repeating each cell into a cell_px x cell_px block.
    Useful to produce a larger image for display (e.g., st.image).
    """
    if cell_px <= 1:
        return rgb_grid.copy()
    return np.kron(rgb_grid, np.ones((cell_px, cell_px, 1), dtype=np.uint8))