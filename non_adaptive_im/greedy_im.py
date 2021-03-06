#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 18:29:52 2018

@author: abhishek.umrawal
"""
from independent_cascade import independent_cascade
from linear_threshold import linear_threshold
import networkx as nx
import numpy as np
import random
import timeit
from true_influence import true_influence
from multiprocessing import Pool
import itertools
from weighted_network import weighted_network

def greedy_im(network, budget, diffusion_model, spontaneous_prob = [], n_sim = 10, num_procs = 1):
    
    np.random.seed(int(random.uniform(0, 1000000)))
    
    """
    Greedy Algorithm for finding the best seed set of a user-specified budget
    
    Inputs:
        - network is a networkx object
        - budget is the user-specified marketing budget which represents the no.
          of individuals to be given the freebies
        - diffusion model is either "independent_cascade" or "linear_threshold"
        - spontaneous_prob is a vector of spontaneous adoption probabiities for
          each node
          
    Outputs:
        - best_seed_set is a subset of the set of nodes with the cardinality  
          same as the budget such that it maximizes the spread of marketing
        - max_influence is the value of maximum influence
  
    """
    J = n_sim
    nodes = list(nx.nodes(network))
    max_influence = []
    best_seed_set = []
    
    if budget == 0:
        
        influence = 0
        
        for j in range(J):
            spontaneously_infected = []
            
            if len(spontaneous_prob) != 0:
                
                for m in range(len(nodes)):
                    
                    if np.random.rand() < spontaneous_prob[m]:
                        spontaneously_infected.append(nodes[m])
                                      
            if diffusion_model == "independent_cascade":
                layers = independent_cascade(network, spontaneously_infected)  
                    
            elif diffusion_model == "linear_threshold":
                layers = linear_threshold(network, spontaneously_infected)    
                    
            for k in range(len(layers)):
                influence = influence + len(layers[k])
                        
        influence = influence/J
        max_influence.append(influence)
        best_seed_set.append(None)
    
    else:
        
        for l in range(budget):
            
            start = timeit.default_timer()
            print('greedy is searching for size '+str(l+1)+' subset')
            
            nodes_to_try = list(set(nodes)-set(best_seed_set))
            influence = np.zeros(len(nodes_to_try))
            
            best_seed_set_plus_ith_node_all = []
            for i in range(len(nodes_to_try)):
                best_seed_set_plus_ith_node = list(set(best_seed_set + [nodes_to_try[i]]))
                best_seed_set_plus_ith_node_all.append(best_seed_set_plus_ith_node)
                
            tmp = [ [network], best_seed_set_plus_ith_node_all, [diffusion_model], [n_sim], [spontaneous_prob] ]
            inputs = itertools.product( *tmp )
            inputs = [tuple(i) for i in inputs]
            #random.seed()
            #random.shuffle(inputs)
            pool = Pool(processes=num_procs)
            influence = list(pool.map(true_influence, inputs))
            #print(influence)
            pool.close()
            pool.join()  
                                
            max_influence.append(np.max(influence))    
            best_seed_set.append(nodes_to_try[np.argmax(influence)])
            
            print(best_seed_set,max_influence)
            
            end = timeit.default_timer()
            print("time taken: " + str(round(end - start,4)) + " seconds")
            
    print('Done!'+'\n')        
    return best_seed_set, max_influence

"Testing"
if __name__ == '__main__':
    import networkx as nx
    import pickle
    import pandas as pd
    
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
    
    #network = nx.florentine_families_graph()
    
    "Converting the subgraph to a directed graph"
    network = network.to_directed()
    
    "Relabeling the nodes as positive integers viz. 1,2,..."
    network = nx.convert_node_labels_to_integers(network,first_label=0)
    
    network = weighted_network(network, 'wc')
    
    nx.write_edgelist(network, "facebook.txt", data=["act_prob"])
    
    x32, y32 = greedy_im(network, 2, 'independent_cascade', num_procs = 1)
    
    data32 = {'best_seed_set':x32, 'max_influence':y32}
    greedy32 = pd.DataFrame.from_dict(data32)
    greedy32.to_csv('greedy32.csv',index=False,header=True)
    