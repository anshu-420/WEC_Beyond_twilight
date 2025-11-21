import pandas as pd
import streamlit as st
import json

def load_CSV_files():
    data = {
        'cells': pd.read_csv(f'/data/cells.csv'),
        'currents': pd.read_csv(f'/data/currents.csv'),
        'hazards': pd.read_csv(f'/data/hazards.csv'),
        'corals': pd.read_csv(f'/data/corals.csv'),
        'food': pd.read_csv(f'/data/food_web.csv'),
        'life': pd.read_csv(f'/data/life.csv'),
        'poi': pd.read_csv(f'/data/poi.csv'),
        'resources': pd.read_csv(f'/data/resources.csv'),
    }

    return data

