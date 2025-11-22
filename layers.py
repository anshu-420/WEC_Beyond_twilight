
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import pygame


@dataclass
class Layer:
	name: str
	grid: List[List[int]]


class Level:
	"""A simple container for layers and a draw helper."""

	def __init__(self, layers: Dict[str, Layer], rows: int = 50, cols: int = 50):
		self.layers = layers
		self.rows = rows
		self.cols = cols

	def draw(self, surface: pygame.Surface, cell_size: int, palette: Optional[Dict[str, tuple]] = None):
		"""Draw non-zero cells for each layer onto `surface`.

		Only draws filled rectangles for non-zero entries.
		"""
		default_palette = {
			'corals': (255, 180, 100),
		}
		pal = {**default_palette, **(palette or {})}

		for lname, layer in self.layers.items():
			color = pal.get(lname, (255, 255, 255))
			for r in range(self.rows):
				for c in range(self.cols):
					try:
						val = layer.grid[r][c]
					except Exception:
						val = 0
					if val and not (pd.isna(val)):
						rect = pygame.Rect(int(c * cell_size), int(r * cell_size), int(cell_size), int(cell_size))
						pygame.draw.rect(surface, color, rect)


def _find_coord_columns(df: pd.DataFrame) -> Optional[tuple]:
	for a, b in (('row', 'col'), ('r', 'c'), ('y', 'x')):
		if a in df.columns and b in df.columns:
			return a, b
	return None


def build_grid_from_df(df: pd.DataFrame, rows: int, cols: int) -> List[List[int]]:
	"""Convert a DataFrame into a rows x cols integer grid.

	Prioritizes explicit coordinate columns. Otherwise attempts to read a
	matrix-like DataFrame (numeric column names or contiguous columns).
	"""
	grid = [[0 for _ in range(cols)] for _ in range(rows)]

	coord = _find_coord_columns(df)
	if coord is not None:
		rcol, ccol = coord
		val_col = None
		for choice in ('value', 'val', 'type', 'id'):
			if choice in df.columns:
				val_col = choice
				break
		for _, row in df.iterrows():
			try:
				r = int(row[rcol])
				c = int(row[ccol])
			except Exception:
				continue
			if 0 <= r < rows and 0 <= c < cols:
				grid[r][c] = int(row[val_col]) if val_col and not pd.isna(row[val_col]) else 1
		return grid

	# matrix-like fallback: use first `cols` columns for each of first `rows` rows
	for r in range(min(rows, len(df))):
		for c in range(min(cols, len(df.columns))):
			try:
				v = df.iloc[r, c]
			except Exception:
				v = 0
			grid[r][c] = int(v) if not pd.isna(v) else 0

	return grid


def build_first_level_corals(rows: int = 50, cols: int = 50, data_dir: Optional[Path | str] = None) -> Level:
	"""Build the first level and fill only the `corals` layer using `load_csv.py`.

	Constraints: does not modify `load_csv.py`. To ensure `load_csv.load_CSV_files()`
	reads from the project's `data/` folder, this function temporarily
	monkeypatches `load_csv.pd.read_csv` to resolve `/data/...` paths to the
	provided `data_dir` (default: `./data`).
	"""
	import load_csv

	base = Path(data_dir) if data_dir is not None else Path(__file__).parent / 'data'
	base = base.resolve()

	# Save original read_csv
	orig_read_csv = load_csv.pd.read_csv

	def _patched_read_csv(path, *args, **kwargs):
		# If path is a string like '/data/corals.csv' or 'data/corals.csv', map to base/name
		try:
			if isinstance(path, (str, Path)):
				p = Path(path)
				name = p.name
				target = base / name
				if target.exists():
					return orig_read_csv(str(target), *args, **kwargs)
		except Exception:
			pass
		# fallback to original
		return orig_read_csv(path, *args, **kwargs)

	try:
		load_csv.pd.read_csv = _patched_read_csv
		data = load_csv.load_CSV_files()
	finally:
		# restore original to avoid side-effects
		load_csv.pd.read_csv = orig_read_csv

	corals_df = data.get('corals') if isinstance(data, dict) else None

	layers: Dict[str, Layer] = {}
	# Create an empty grid for corals if DF missing
	if isinstance(corals_df, pd.DataFrame):
		coral_grid = build_grid_from_df(corals_df, rows, cols)
	else:
		coral_grid = [[0 for _ in range(cols)] for _ in range(rows)]

	layers['corals'] = Layer(name='corals', grid=coral_grid)

	return Level(layers=layers, rows=rows, cols=cols)


if __name__ == '__main__':
	# Quick local smoke example (won't run correctly within tests but is useful as a manual check)
	print('Building first level corals from ./data (if available)')
	lvl = build_first_level_corals()
	print('Built level with layers:', list(lvl.layers.keys()))

