#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 23 13:33:30 2020

@author: abhishek.umrawal
"""
import networkx as nx
import pickle
#import numpy as np
#import pandas as pd
import scipy
import os
#from stoch_dom import stoch_dom
from nchoosek import nchoosek
#from ecdf import ecdf
from matplotlib import pyplot as plt
plt.rcParams['figure.figsize'] = [4.6,3.6]
import random
import timeit

"IMPORTANT: keep it 1234"
random.seed(1234)

"""Working with the Facebook network """
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

"Working with a subgraph after deleting an outlier node"
nodes_subset.remove(1684)
network = nx.subgraph(network, nodes_subset)

"""Working with the Florentine families network """
"Declaring the Florentine families network"
#network = nx.florentine_families_graph()

"Converting the subgraph to a directed graph"
network = network.to_directed()

"Relabeling the nodes as positive integers viz. 1,2,..."
network = nx.convert_node_labels_to_integers(network,first_label=1)

"inputs:"
weighting_scheme = 'wc'
diffusion_model = 'independent_cascade'
spontaneous_prob = []
seed_set_sizes = [2,4,8]
name_id = '_fb4_new'
is_network_small = 'no' #if 'yes' then exhaustive -- no sampling
num_ab_pairs = 100*5 # 500 for _fb4_new
num_S = 50*10 # 500 for _fb4_new
m = 1.1+1.9 # 3 for _fb4_new #set m to a least upper bound such that the code finishes -- play with the number after + 

"defining the a,b pairs"
if is_network_small == 'yes':
    ab_pairs = nchoosek(len(network.nodes()),2)
else:
    ab_pairs = []
    while len(ab_pairs) < num_ab_pairs:
        ab_pair = random.sample(network.nodes,2)
        if not ab_pair in ab_pairs:
            ab_pairs+=[ab_pair]

"saving ab_pairs as a pickle file in part1 folder within results<name_id> folder"
if not os.path.exists('results'+name_id+os.sep+'part1'):
    os.makedirs('results'+name_id+os.sep+'part1')
filename = 'ab_pairs.pkl'      
fstr = 'results'+name_id+os.sep+'part1'+os.sep+filename
with open(fstr,'wb') as f:
    pickle.dump(ab_pairs, f)

"defining a dictionary of  master lists of k-1 subsets for different k"
master_S_subsets = {}
for k in seed_set_sizes:
    subsets = []                
    for i in range(0,int(num_S*m)):
        subsets.append(random.sample(network.nodes,k-1))
    master_S_subsets[k] = subsets

"defining the k-1 size subsets for different k relative to the pair a,b"
"drawn from the corresponding master list in case of non _fl networks"
print("part 1: defining the k-1 size subsets for different k relative to the pair a,b")
S_subsets = {}
for i,[a,b] in enumerate(ab_pairs):
    all_nodes = list(network.nodes)
    all_nodes.remove(a)
    all_nodes.remove(b)
    for k in seed_set_sizes:
        subsets = []
        if is_network_small == 'yes':
            num_S = int(scipy.special.comb(len(network.nodes)-2,k-1))    
            while len(subsets) < num_S:
                subset = set(sorted(random.sample(all_nodes,k-1)))
                if not subset in subsets:
                    subsets.append(subset)
        else:  
            while len(subsets) < num_S:
                subset = set(sorted(random.choice(master_S_subsets[k])))
                if not a in subset and not b in subset and not subset in subsets:
                    subsets.append(subset)
        S_subsets[((a,b),k)] = subsets
    if not i % 50:
        print('rem steps in part 1: '+str(num_ab_pairs-i-1))
        
"saving S_subsets as a pickle file in part1 folder within results<name_id> folder"
if not os.path.exists('results'+name_id+os.sep+'part1'):
    os.makedirs('results'+name_id+os.sep+'part1')
filename = 's_subsets.pkl'      
fstr = 'results'+name_id+os.sep+'part1'+os.sep+filename
with open(fstr,'wb') as f:
    pickle.dump(S_subsets, f)

"constructing all S_union_x where x in {a,b} kind subsets for all k"
print("part 2: constructing all S_union_x where x in {a,b} kind subsets for all k")
S_union_x_subsets = []
for i,((a,b),k) in enumerate(S_subsets.keys()):
    start = timeit.default_timer()
    for S in S_subsets[((a,b),k)]:
        if S.union({a}) not in S_union_x_subsets:
            S_union_x_subsets.append(set(sorted(S.union({a}))))
        if S.union({b}) not in S_union_x_subsets:
            S_union_x_subsets.append(set(sorted(S.union({b}))))
            
    end = timeit.default_timer()
    if not i % 50:
        print('rem steps in part 2: '+str(num_ab_pairs*len(seed_set_sizes)-i-1)+' time taken at the current step: ' + str(round(end - start,4)) + ' seconds')
print('total no. of unique subsets: '+str(len(S_union_x_subsets)))  

"saving S_union_x_subsets as a pickle file in inputs_<name_id> folder in ../exp_influences"
if not os.path.exists('../exp_influences'+os.sep+'inputs'+name_id):
    os.makedirs('../exp_influences'+os.sep+'inputs'+name_id)
filename = 's_union_x_subsets.pkl'      
fstr = '../exp_influences/inputs'+name_id+os.sep+filename
with open(fstr,'wb') as f:
    pickle.dump(S_union_x_subsets, f)
    