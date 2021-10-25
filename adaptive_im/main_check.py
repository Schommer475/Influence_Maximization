#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 19:17:14 2019

@author: abhishek.umrawal
"""

"Importing necessary modules"
from influence import influence
from weighted_network import weighted_network
import networkx as nx
import os as os; os.getcwd()
import pickle
import numpy as np

"Reading the Facebook network from file"
network = nx.read_edgelist("facebook_network.txt",create_using=nx.DiGraph(), nodetype = int)

"Reading communities"
filename = 'communities.pkl'
with open(filename, 'rb') as f:
    part = pickle.load(f)
value = [part.get(node) for node in network.nodes()]
nodes_subset = [key for key,value in part.items() if value == 4]
    
"Working with a subgraph"
network = nx.subgraph(network, nodes_subset)

"Declaring the Florentine families network"
network = nx.florentine_families_graph()

"Converting the subgraph to a directed graph"
network = network.to_directed()

"Relabeling the nodes as positive integers viz. 1,2,..."
network = nx.convert_node_labels_to_integers(network,first_label=1)

"Adding weights to the network"
network = weighted_network(network, 'wc')

"Inputs"
diffusion_model = 'independent_cascade' # 'linear_threshold'
spontaneous_prob = []

seed_sets = [[533, 529, 528, 527, 530, 532, 531, 228], [533, 527, 528, 529], [533,527], [533]]

seed_sets = [[2,1,8,9]]
influences = []

for seed_set in seed_sets:
    influences.append(np.mean([influence(network, seed_set, diffusion_model, spontaneous_prob = []) for i in range(0,1000)]))

print(influences)