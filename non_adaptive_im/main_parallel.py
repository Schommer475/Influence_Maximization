#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 05:50:12 2020

@author: abhishek.umrawal
"""

from multiprocessing import Pool
import itertools
import random
from true_influence import true_influence
from weighted_network import weighted_network
from greedy_im import greedy_im
import networkx as nx

num_procs = 1

"example 1"
def my_fun(a):
    return a[0]*a[1]

tmp = [ [2], [2,3,4,5]]
inputs = itertools.product( *tmp )
inputs = [tuple(i) for i in inputs]
random.seed()
random.shuffle(inputs)
pool = Pool(processes=num_procs)
influence = list(pool.map(my_fun, inputs))
pool.close()
pool.join()  
print(influence)


"example 2"
network = nx.florentine_families_graph()
network = network.to_directed()
network = nx.convert_node_labels_to_integers(network,first_label=1)
network = weighted_network(network,'wc')
diffusion_model = 'independent_cascade'
seed_sets = [[1],[2],[3]]
n_sim = 10
spontaneous_prob = []

for i in range(0,5):
    tmp = [ [network], seed_sets, [diffusion_model], [n_sim], [spontaneous_prob]]
    inputs = itertools.product( *tmp )
    inputs = [tuple(i) for i in inputs]
    random.seed()
    random.shuffle(inputs)
    pool = Pool(processes=num_procs)
    influence = list(pool.map(true_influence, inputs))
    pool.close()
    pool.join()  
    print(influence)


"example 3"
budget = 2
greedy_im(network, budget, diffusion_model, spontaneous_prob, n_sim, num_procs)
