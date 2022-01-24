#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 19:17:14 2019

@author: abhishek.umrawal
"""

"Importing necessary modules"
from weighted_network import weighted_network
import networkx as nx
import os as os; os.getcwd()
import pickle
from optimal_im import optimal_im
import numpy as np
from influence import influence
 
name_id = '_fl'

"Reading the Facebook network from file"
network = nx.read_edgelist("facebook_network.txt",create_using=nx.DiGraph(), nodetype = int)

"Reading communities"
filename = 'communities.pkl'
with open(filename, 'rb') as f:
    part = pickle.load(f)
value = [part.get(node) for node in network.nodes()]
nodes_subset = [key for key,value in part.items() if value == 4]
    
"Working with a subgraph after deleting an outlier node"
nodes_subset.remove(1684)
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
seed_set_sizes = [2,4,8]
spontaneous_prob = []
n_sim = 1

"Optim IM calculations"
optimal_im_res = {}

if name_id == '_fl':
    try:
        filename = '../exp_influences/results'+name_id+os.sep+'exp_influences_dict.pkl'
        with open(filename, 'rb') as f:
            influence_dict = pickle.load(f)
    except:
        influence_dict = {}
    
    for budget in seed_set_sizes:
        fun_out = optimal_im(network, budget, diffusion_model, n_sim, influence_dict, spontaneous_prob)
        optimal_im_res[budget] = [fun_out[0],fun_out[1]]
    

if name_id != '_fl':    
    seed_sets = [[533,527], [533, 527, 528, 529], [533, 529, 528, 527, 530, 532, 531, 228]]
    for seed_set in seed_sets:
        optimal_im_res[len(seed_set)] = [seed_set, np.mean([influence(network, seed_set, diffusion_model, spontaneous_prob = []) for i in range(0,10)])]

"Saving the results as a pickle file"
fstr = 'results'+name_id+os.sep+'optimal_im_res.pkl'
with open(fstr,'wb') as f:
    pickle.dump(optimal_im_res, f)
    
    
