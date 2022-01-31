#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 19:17:14 2019

@author: abhishek.umrawal
"""

"importing required built-in modules"
import itertools
import networkx as nx
import pickle
import timeit
from Utilities.global_names import resources, facebook_network, communities
import os
#import random

"importing required user-defined modules"
from non_adaptive_im import non_adaptive_im

def main():

    "start time"
    start = timeit.default_timer()
    
    "multiprocessing parameter for greedy_im -- not used otherwise"
    num_procs = 1
    
    """working with the Facebook network """
    "reading the Facebook network from file"
    facebook_path = os.path.join(resources, facebook_network)
    network = nx.read_edgelist(facebook_path,create_using=nx.DiGraph(), nodetype = int)
    
    "reading communities"
    communities_path = os.path.join(resources, communities)
    with open(communities_path, 'rb') as f:
        part = pickle.load(f)
    value = [part.get(node) for node in network.nodes()]
    nodes_subset = [key for key,value in part.items() if value == 4]
       
    "working with a subgraph after deleting an outlier node"
    nodes_subset.remove(1684)
    network = nx.subgraph(network, nodes_subset)
    
    """working with the Florentine families network """
    "declaring the Florentine families network"
    network = nx.florentine_families_graph()
    #network = nx.karate_club_graph()
    
    "converting the subgraph to a directed graph"
    network = network.to_directed()
    
    "relabeling the nodes as positive integers viz. 1,2,..."
    network = nx.convert_node_labels_to_integers(network,first_label=1)
    
    "inputs for non_adaptive_im"
    seed_set_sizes = [8] # just provide the max seed set size
    diffusion_model = ['independent_cascade'] # 'linear_threshold'
    weighting_scheme = ['wc'] # 'tv' 'rn'
    algorithms =  ['degree','wdegree','greedy'] 
    name_id = ['_fl_inv']
    n_sim = [1000]
    
    "create a list of all parameter lists, then use product"
    tmp = [ [network], weighting_scheme, seed_set_sizes, diffusion_model, algorithms, n_sim, [num_procs], name_id ]
    inputs = itertools.product( *tmp )
    inputs = [tuple(i) for i in inputs]
    #random.seed()
    #random.shuffle(inputs)
    
    "call non_adaptive_im for all input combinations -- no parallelization"
    "python doesn't allow daemon processes to have children"
    "there is already parallelization in greedy_im"
    for inpt in inputs:
        print('I am running '+inpt[4]+'_im:')
        non_adaptive_im(inpt)
    
    "end time"
    end = timeit.default_timer()
    
    "time taken"
    print("Time taken: " + str(round(end - start,4)) + " seconds")
