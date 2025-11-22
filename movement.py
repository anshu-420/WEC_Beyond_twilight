#Team Name: Anything Works

import streamlit as st
import pandas as pd
import numpy as np
import random
from load_csv import DataLoader
import math

directions = {
    'N': (0, 1),
    'NE': (1, 1),
    'E': (1, 0),
    'SE': (1, -1),
    'S': (0, -1),
    'SW': (-1, -1),
    'W': (-1, 0),
    'NW': (-1, 1)
}

class MovementSimulator:
    def __init__(self, data):
        self.data = data

    def get_current_at_position(self, x, y):
        """Retrieve current data at a specific (x, y) position."""
        currents = self.data['currents']
        col = math.floor(x / 4)
        row = math.floor(y / 4)
        print(col, row)
        current_info = currents[(currents['col'] == col) & (currents['row'] == row)]
        if not current_info.empty:
            return current_info.iloc[0].to_dict()
        return None
    
    def next_position(self, x, y):
        """Calculate the next position based on current data."""
        current = self.get_current_at_position(x, y)
        dir = random.choice(list(directions.values()))
        print(dir);
        if current:
            def round_by_threshold(value, threshold=0.5):
                frac = value - math.floor(value)
                if frac > threshold:
                    return math.ceil(value)
                return math.floor(value)

            print(x + dir[0] * current['u_mps'], y + dir[1] * current['v_mps'] )
            new_x = round_by_threshold(x + dir[0] * current['u_mps'])
            new_y = round_by_threshold(y + dir[1] * current['v_mps'])
            return new_x, new_y
        return x, y


loader = DataLoader()
data = loader.load_CSV_files()

simulator = MovementSimulator(data)
print(simulator.get_current_at_position(5, 10))
print(simulator.next_position(5, 10))