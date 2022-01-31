#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 21:39:24 2018

@author: abhishek.umrawal
"""
from Utilities.independent_cascade import independent_cascade
from Utilities.linear_threshold import linear_threshold
from Utilities.global_names import resources, facebook_network, communities
from os.path import join as join_path
import networkx as nx
import numpy as np
from tqdm import tqdm

def influence(network, seed_set, diffusion_model, spontaneous_prob = []):
    
    nodes = list(nx.nodes(network))
    influence = 0
            
    spontaneously_infected = []
        
    if len(spontaneous_prob) != 0:
        for m in range(len(network)):
            if np.random.rand() < spontaneous_prob[m]:
                spontaneously_infected.append(nodes[m])
                    
        
    if diffusion_model == "independent_cascade":
        layers = independent_cascade(network, list(set(spontaneously_infected + seed_set)))  
        
    elif diffusion_model == "linear_threshold":
        layers = linear_threshold(network, list(set(spontaneously_infected + seed_set)))    
        
    for k in range(len(layers)):
        influence = influence + len(layers[k])

    return influence

def main():
    import pickle
    import pandas as pd
    
    """----------------------------------"""
    """READING/INTIALIZING THE NETWORK"""
    """Working with the Facebook network """
    "Reading the Facebook network from file"
    facebook_path = join_path(resources,facebook_network)
    network = nx.read_edgelist(facebook_path,create_using=nx.DiGraph(), nodetype = int)
    
    "Reading communities"
    filename = 'communities.pkl'
    communities_path = join_path(resources,communities)
    with open(communities_path, 'rb') as f:
        part = pickle.load(f)
    value = [part.get(node) for node in network.nodes()]
    nodes_subset = [key for key,value in part.items() if value == 4]
       
    "Working with a subgraph after deleting an outlier node"
    nodes_subset.remove(1684)
    network = nx.subgraph(network, nodes_subset).copy() # .copy() makes a subgraph with its own copy of the edge/node attributes
    
    #network = nx.florentine_families_graph()
    
    "Converting the subgraph to a directed graph"
    network = network.to_directed()
    
    "Relabeling the nodes as positive integers viz. 1,2,..."
    network = nx.convert_node_labels_to_integers(network,first_label=0)

    #celf_solution, celf_spreads, celf_elapsed, celf_lookups = celf(network, 32)
    
#    print('solution: ', celf_solution)
#    print('spreads: ', celf_spreads)
#    print('elapsed: ', celf_elapsed)
#    print('lookups: ', celf_lookups)
    
    #celf_solution = [0, 34, 45, 41, 53, 36, 2, 17, 527, 7, 33, 4, 56, 60, 227, 6]
    ucbgr_solution = [1, 3, 35, 528, 4, 228, 46, 338, 42, 7, 54, 2, 37, 31, 30, 527]
#    
#    #celf1 = compute_independent_cascade(network, celf_solution, 0.1, 10000)
#    ucbgr4000 = influence(network, ucbgr_solution, "independent_cascade")
#    print(ucbgr4000)
#    
    all_inf=0
    for i in tqdm(range(1000)):
        all_inf+=influence(network, ucbgr_solution, "independent_cascade")
        
    print(all_inf/1000)

