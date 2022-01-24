#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 17:37:20 2019

@author: cjquinn
"""

if __name__ == '__main__':
    import random
    from multiprocessing import Pool
    import itertools
    from adaptive_im import adaptive_im
    #from subgraph import subgraph
    import networkx as nx
    import pickle
    import timeit
    import IMLinUCB
    import os
    
    "Start time"
    start = timeit.default_timer()
    
    "Input and output directories (NEED to be defined in adaptive_im and e-CD methods)"
    #input_dir = '/scratch/brown/aumrawal/jmlr2020-new/adaptive_im'
    #output_dir = '/home/aumrawal/jmlr2020-new/adaptive_im'
    
    input_dir = os.getcwd()
    print(input_dir)
    output_dir = '/scratch/brown/nieg/'
    
    "Multiprocessing parameter"
    num_procs = 20
    
    """----------------------------------"""
    """READING/INTIALIZING THE NETWORK"""
    """Working with the Facebook network """
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
    network = nx.subgraph(network, nodes_subset).copy() # .copy() makes a subgraph with its own copy of the edge/node attributes
    
    """Working with the Florentine families network """
    "Declaring the Florentine families network"
    network = nx.florentine_families_graph()
    #network = nx.karate_club_graph()
    """----------------------------------"""
    
    "Converting the subgraph to a directed graph"
    network = network.to_directed()
    
    "Relabeling the nodes as positive integers viz. 1,2,..."
    network = nx.convert_node_labels_to_integers(network,first_label=1)
    
    """----------------------------------"""
    "Inputs for adaptive_im"
    seed_set_sizes = [4]                   # [2,4,6,8] # list of seed set sizes
    num_times = [10000]                        # [100000] # time horizon for the online algorithms
    num_samples = [10]                         # [5,10,20,30] # list of values of C for adgr, lower the C, lower the exploration
    stage_horizon = [1000]                       # [100,200] # stage horizon for the ucbgr algorithm
    #print('num_times: '+str(num_times[0]))
    diffusion_model = ['independent_cascade']  # ['independent_cascade', 'linear_threshold'] # diffusion models
    weighting_scheme = ['un']                  # ['wc', 'un', 'tv','rn'] # weighting schemes
    algorithms =  ['dart', 'cmab', 'ucbgr']                    # ['adgr1','cmab','csar','dart','ecd2','ucb','rand'] # algorithms
    epsilons = [1]                             # [0.10, 0.25, 1] #exploration parameter for ecd_im and adgr_im, keep it 1 for adgr_im for now
    name_id = ['_fb4_un']                         # ['_fl','_fb4_new'] # identifier to name the output folder as results_<name_id>
    num_runs = 10                               # 10 # for each algorithm, seed set size, etc. the number of runs
    df_feats = IMLinUCB.generate_node2vec_fetures(graph=network, dataset_name = "facebook", node2vec_path = "node2vec.exe")
                                            #inputs for imlinucb
    """----------------------------------"""
    
    """Notes on Inputs"""
    # all inputs are in list format except num_runs
    # numeric inputs are entered as numeric
    
    "map inputs"
    seed_set_sizes = seed_set_sizes*num_runs
    
    "create a list of all parameter lists, then use product"
    tmp = [ [network], weighting_scheme, seed_set_sizes, epsilons, diffusion_model, num_times, num_samples, stage_horizon, algorithms, name_id]
    inputs = itertools.product( *tmp )
    
    #inputs = [tuple(i) for i in inputs]
    l = [list(i) for i in inputs]
    for i in range(len(l)):
        l[i].append(df_feats)
        
    inputs = [tuple(i) for i in l]
    
    random.seed()
    random.shuffle(inputs)
    
    "parallelization"
    pool = Pool(processes=num_procs)
    
    pool.map(adaptive_im, inputs)
    
    pool.close()
    pool.join()     
    
    "End time"
    end = timeit.default_timer()
    
    "Time taken"
    print("Time taken: " + str(round(end - start,4)) + " seconds")
