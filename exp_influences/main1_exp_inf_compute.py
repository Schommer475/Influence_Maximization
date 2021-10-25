#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 19:17:14 2019

@author: abhishek.umrawal
"""

"Importing necessary modules"
from true_influence import true_influence
#from nchoosek import nchoosek
from weighted_network import weighted_network
import time as time
import networkx as nx
import os as os; os.getcwd()
import pickle
from multiprocessing import Pool
import itertools
import timeit
    
start_time = timeit.default_timer()

"Multiprocessing parameter"
num_procs = 3

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
diffusion_model = ['independent_cascade'] # 'linear_threshold'
spontaneous_prob = [[]]
n_sim = [1]
name_id = ['_fl']

#"Calculating expected influence and saving to a pickle file"
#"Checking if it exists in the collate folder and the appending in the same file"
#filename = 'results'+name_id[0]+os.sep+'exp_influences_dict.pkl'
#if os.path.exists(filename):
#    with open(filename, 'rb') as f:
#        exp_influences_dict = pickle.load(f)
#else:
#    exp_influences_dict = {}
    
#"defining a list of all seed sets"
#seed_sets = []
#seed_set_sizes = [2,4,8]
#num_samples = 10
#if name_id[0] == '_fl':
#    for seed_set_size in seed_set_sizes:
#        seed_sets += nchoosek(len(network.nodes()),seed_set_size)
#elif name_id[0] == '_fb4':
#    for seed_set_size in seed_set_sizes:
#        for i in range(0,seed_set_size*num_samples):
#            seed_sets += [random.sample(network.nodes,seed_set_size)]

"reading seed sets dictionary"
filename = 'inputs'+name_id[0]+os.sep+'s_union_x_subsets.pkl'
with open(filename, 'rb') as f:
    seed_sets=pickle.load(f)
seed_sets = [list(x) for x in seed_sets]
print('total seed sets: '+str(len(seed_sets)))

#"removing the seed sets from sees_sets which are already in exp_influences_dict"
#for seed_set in seed_sets:
#    if seed_set in [list(item) for item in list(exp_influences_dict.keys())]:
#        seed_sets.remove(seed_set)

"partition the seed_sets list into smaller lists to submit jobs on different machines"
num_chunks = 10 # ACTUAL No. CAN BE ONE MORE
try: 
    seed_sets_chunks = [seed_sets[x:x+int(len(seed_sets)/num_chunks)] for x in range(0, len(seed_sets), int(len(seed_sets)/num_chunks))]
except:
    seed_sets_chunks = [seed_sets]

"selecting a chunk of seed sets"
which_chunks = list(range(0,10+1)) # USER-INPUT: can range from 0 to num_chunks-1

for i in which_chunks:
    starti = timeit.default_timer()
    chosen_seed_sets_chunk = seed_sets_chunks[i]
    print('\n'+'trying all '+ str(len(chosen_seed_sets_chunk))+' seed sets from chunk ' + str(i))
    
    "partition chosen_seed_sets_chunk further into smaller lists for periodic saving of results as pickle files"
    num_sub_chunks = 5
    try: 
        seed_sets_sub_chunks = [chosen_seed_sets_chunk[x:x+int(len(chosen_seed_sets_chunk)/num_sub_chunks)] for x in range(0, len(chosen_seed_sets_chunk), int(len(chosen_seed_sets_chunk)/num_sub_chunks))]
    except:
        seed_sets_sub_chunks = [chosen_seed_sets_chunk]
    
    "looping over all sub chunks within a chunk"
    exp_influences_dict = {}
    for j,seed_sets_sub_chunk in enumerate(seed_sets_sub_chunks):
        startj = timeit.default_timer()
        print('trying all '+ str(len(seed_sets_sub_chunk))+' seed sets from sub chunk ' + str(j) +' of chunk '+str(i))
        "create a list of all parameter lists, then use product"
        tmp = [ [network], seed_sets_sub_chunk, diffusion_model, n_sim, spontaneous_prob, name_id]
        inputs = itertools.product( *tmp )
        inputs = [tuple(i) for i in inputs]
        
        "parallelization"
        pool = Pool(processes=num_procs)
        exp_influences_list = list(pool.map(true_influence, inputs))
        pool.close()
        pool.join()  
        
        "saving exp_influences_list as a dictionary"
        for [seed_set,exp_influence] in exp_influences_list:
            exp_influences_dict[tuple(sorted(set(seed_set)))] = exp_influence
            
        "saving the expected influences dictionary as a pickle file"
        if not os.path.exists('results'+name_id[0]+os.sep+'compute'):
            os.makedirs('results'+name_id[0]+os.sep+'compute')
            
        results = {'diffusion_model':diffusion_model,'n_sim':n_sim,'spontaneous_prob':spontaneous_prob,'name_id':name_id,'exp_influences_dict':exp_influences_dict}
            
        fstr = 'results'+name_id[0]+os.sep+'compute'+os.sep+'exp_influences_dict_'+str(i)+'_'+str(j)+'.pkl'
        with open(fstr,'wb') as f:
            pickle.dump(results, f)
        endj = timeit.default_timer()
        print("time taken = "+str(round(endj - startj,2))+' seconds')
    
    endi = timeit.default_timer()
    print("time taken = "+str(round(endi - starti,2))+' seconds')
    
end_time = timeit.default_timer()
print('\n'+"total time taken = "+str(round(end_time - start_time,2))+' seconds')


