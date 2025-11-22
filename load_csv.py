import os
import pandas as pd
import streamlit as st
import json

class DataLoader:
    def load_CSV_files(self):
        base_dir = os.path.join(os.path.dirname(__file__), 'data')
        data = {
            'cells': pd.read_csv(os.path.join(base_dir, 'cells.csv')),
            'currents': pd.read_csv(os.path.join(base_dir, 'currents.csv')),
            'hazards': pd.read_csv(os.path.join(base_dir, 'hazards.csv')),
            'corals': pd.read_csv(os.path.join(base_dir, 'corals.csv')),
            'food': pd.read_csv(os.path.join(base_dir, 'food_web.csv')),
            'life': pd.read_csv(os.path.join(base_dir, 'life.csv')),
            'poi': pd.read_csv(os.path.join(base_dir, 'poi.csv')),
            'resources': pd.read_csv(os.path.join(base_dir, 'resources.csv')),
        }

        return data

