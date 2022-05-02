# %%
from collections import defaultdict
import pandas as pd
import numpy as np

data_nodes = pd.read_excel('input.xlsx', sheet_name='nodes')
data_distances = pd.read_excel('input.xlsx', sheet_name='distances')


def generate_model_data(data_nodes, data_distances):
    # Create set of nodes
    nodes = {i for i in data_nodes['node']}

    # Create set of edges
    edges = {(data_distances['from'][i], data_distances['to'][i])
             for i in range(len(data_distances['from']))}

    # Create distances
    distance = {(data_distances['from'][i], data_distances['to'][i]):data_distances['distance'][i] for i in range(len(data_distances['from']))}

    # Create V's sets
    v_in = defaultdict(set)
    v_out = defaultdict(set)

    for (i, j) in edges:
        v_in[j].add(i)
        v_out[i].add(j)

    return nodes, edges, distance, v_in, v_out


def generate_parameters():

    nodes, edges, distance, v_in, v_out = generate_model_data(
        data_nodes, data_distances)
    return nodes, edges, distance, v_in, v_out
