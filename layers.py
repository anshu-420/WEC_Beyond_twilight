#Team Name: Anything Works

from load_csv import DataLoader
import numpy as np

def assignRandomLayers(data):

    corals = data['corals']
    corals['layer'] = np.random.randint(2, 6, size=len(corals))
    # print(corals[:20])

    foodWeb = data['food_web']
    foodWeb['layer'] = np.random.randint(3, 6, size=len(foodWeb))
    # print(foodWeb[:20])

    hazards = data['hazards']
    hazards['layer'] = np.random.randint(4, 6, size=len(hazards))
    # print(hazards[:20])

    life = data['life']
    life['layer'] = np.random.randint(3, 6, size=len(life))
    # print(life[:20])

    poi = data['poi']
    poi['layer'] = np.random.randint(2, 6, size=len(poi))
    # print(poi[:20])

    resources = data['resources']
    resources['layer'] = np.random.randint(6, 7, size=len(resources))
    # print(resources[:20])

    
    return data


def getObjects(layer):
    loader = DataLoader()
    data = loader.load_CSV_files()
    
    data = assignRandomLayers(data)

    objects_in_layer = {}
    
    for obj_type in ['corals', 'food_web', 'hazards', 'life', 'poi', 'resources']:
        df = data[obj_type]
        filtered = df[df['layer'] == layer]
        objects_in_layer[obj_type] = filtered

    return objects_in_layer
