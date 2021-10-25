#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 23 12:24:12 2020

@author: abhishek.umrawal
"""

import numpy as np
import networkx as nx
#from true_influence import true_influence
from weighted_network import weighted_network

#function to ignore division by zero
def div(n,d):
    return n/d if d else 0

def stoch_dom(network, weighting_scheme, diffusion_model, spontaneous_prob, n_sim, k, S_list, a, b, influences_dict={}):
    
    network = network.to_directed()
    network = nx.convert_node_labels_to_integers(network,first_label=1)
    network = weighted_network(network,method = weighting_scheme)
    
    n = len(network.nodes)
    
    all_arms = list(range(1,n+1))
    for element in [a,b]:
        all_arms.remove(element)
    
    rewards_S_union_a = []
    rewards_S_union_b = []
    for S in S_list:
        S_union_a = S.union({a})
        S_union_b = S.union({b})
    
        if (tuple(sorted(S_union_a)) in influences_dict.keys() and tuple(sorted(S_union_b)) in influences_dict.keys()):
            rewards_S_union_a.append(influences_dict[tuple(sorted(S_union_a))])
            rewards_S_union_b.append(influences_dict[tuple(sorted(S_union_b))])
        else:
            #rewards_S_union_a.append(true_influence([network, S_union_a, diffusion_model, spontaneous_prob, n_sim]))
            #rewards_S_union_b.append(true_influence([network, S_union_b, diffusion_model, spontaneous_prob, n_sim]))
            print(str(a)+' '+str(b)+' '+str(k)+' '+str(tuple(sorted(S_union_a)))+' '+str(tuple(sorted(S_union_b))))
            continue
    
    with_prob = div(sum(list(np.array(rewards_S_union_a)>np.array(rewards_S_union_b))),len(rewards_S_union_a))
    
    if with_prob > 0.5:
        return [str(k), "S_union_"+str(a)+" > "+"S_union_"+str(b), with_prob]
    else:
        return [str(k), "S_union_"+str(b)+" > "+"S_union_"+str(a), 1-with_prob]