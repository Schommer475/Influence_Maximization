#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 23 13:33:30 2020

@author: abhishek.umrawal
"""
import networkx as nx
import pickle
import numpy as np
import pandas as pd
import os
from stoch_dom import stoch_dom
from ecdf import ecdf
from matplotlib import pyplot as plt
plt.rcParams['figure.figsize'] = [4.6,3.6]

import tikzplotlib

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
n_sim = 5
seed_set_sizes = [2,4,8]
name_id = '_fb4_new'

"reading a,b pairs"        
filename = 'ab_pairs.pkl'      
fstr = 'results'+name_id+os.sep+'part1'+os.sep+filename
with open(fstr, 'rb') as f:
    ab_pairs = pickle.load(f)

"reading S_subsets from results<name_id>/part1 folder which is the output on main1_stoch_dom.py"
filename = 's_subsets.pkl'      
fstr = 'results'+name_id+os.sep+'part1'+os.sep+filename
with open(fstr, 'rb') as f:
    S_subsets = pickle.load(f)

"reading existing influences dictionary"
filename = '../exp_influences'+os.sep+'results'+name_id+os.sep+'exp_influences_dict.pkl'
with open(filename, 'rb') as f:
    influences_dict = pickle.load(f)
          
"calling the stoch_dom function for different seed set sizes"        
with_probs = {}
for k in seed_set_sizes:
    with_probs[k] = []
    for i,[a,b] in enumerate(ab_pairs):
        S_list = [set(sorted(x)) for x in S_subsets[((a,b),k)]]          
        fun_out = stoch_dom(network, weighting_scheme, diffusion_model, spontaneous_prob, n_sim, k, S_list, a, b, influences_dict)
        with_probs[k].append(fun_out[2])

"ecdf calculation -- ecdf is complementary empirical CDF"
with_probs_ecdf = pd.DataFrame()
bins = list(np.linspace(0.5,1,100000))
for key in with_probs.keys():
    _,with_probs_ecdf[str(key)] = ecdf(with_probs[key],bins=bins)

"plotting"    
with_probs_ecdf.index = bins
 
ax = with_probs_ecdf.plot(lw=3)
ax.set_xlabel('1 - $\delta$')
ax.set_ylabel("Complementary CDF")
ax.legend(['$K$ = 2','$K$ = 4','$K$ = 8'])
ax.grid(linestyle='-', linewidth=1)

if not os.path.exists('results'+name_id+os.sep+'part2'):
    os.mkdir('results'+name_id+os.sep+'part2')
ax.get_figure().savefig('results'+name_id+os.sep+'part2'+'/stoch_dom'+name_id+'.eps')
ax.get_figure().savefig('results'+name_id+os.sep+'part2'+'/stoch_dom'+name_id+'.jpg')

"saving as a .tex to be used in latex documents"
tikzplotlib.clean_figure()
tikzplotlib.save('results'+name_id+os.sep+'part2'+os.sep+'/stoch_dom'+name_id+'.tex')
