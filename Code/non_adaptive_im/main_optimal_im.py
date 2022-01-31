#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 19:17:14 2019

@author: abhishek.umrawal
"""

"Importing necessary modules"
from Utilities.weighted_network import weighted_network
import networkx as nx
import os as os; os.getcwd()
import pickle
from non_adaptive_im.optimal_im import optimal_im
import numpy as np
from Utilities.influence import influence
from Utilities.global_names import resources, facebook_network, communities, non_adaptive_temp
 
def main():
    name_id = '_fl'
    
    "Reading the Facebook network from file"
    facebook_path = os.path.join(resources, facebook_network)
    network = nx.read_edgelist(facebook_path,create_using=nx.DiGraph(), nodetype = int)
    
    "Reading communities"
    communities_path = os.path.join(resources, communities)
    with open(communities_path, 'rb') as f:
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
            #TODO find out if this part is still relevant or if I got rid of files I shouldn't have.
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
    output_dir = non_adaptive_temp
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    output_dir = os.path.join(output_dir, "results" + name_id)
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    fstr = os.path.join(output_dir,'optimal_im_res.pkl')
    with open(fstr,'wb') as f:
        pickle.dump(optimal_im_res, f)
    
    
