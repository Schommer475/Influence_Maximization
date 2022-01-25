#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 18 02:23:56 2019

@author: abhishek.umrawal
"""

"Importing necessary modules"
from Utilities.influence import influence
import numpy as np
import os as os; os.getcwd()
import random
from collections import defaultdict 
import operator

def adgr1_im(network, seed_set_size, diffusion_model, num_times, num_samples, epsilon):
    
    np.random.seed(int(random.uniform(0, 1000000)))
    
    "reward/influence function"
    def reward(arms_list):
        return influence(network, arms_list, diffusion_model, spontaneous_prob=[])
    
    "ignore division by zero"
    def div(n,d):
        return n/d if d else 0 
    
    "num_sample multiplier"
    def M(N,K):
        return sum([N-k for k in range(0,K)])
    
    N = len(network.nodes)
    K = seed_set_size
    T = num_times
    num_samples = int(min(num_samples, T/M(N,K)))
    A = list(range(1,N+1))
    #random.shuffle(A)
    
    best_seed_sets_adgr = []
    obs_influences_adgr = []
    accept_set = set()
    
    avg_cumulative_rewards =  defaultdict(int)
    counts = defaultdict(int)
    
    for k in range(1,K+1):
        #print(range(M(N,k-1)*num_samples, M(N,k)*num_samples))
        for t in range(M(N,k-1)*num_samples, M(N,k)*num_samples): 
            
            if t == M(N,k-1)*num_samples or random.uniform(0,1) < epsilon:
                index = t % (N - len(accept_set)) 
                arm = A[index]
                chosen_arms = accept_set.union({arm})   
            else:
                avg_cumulative_rewards_k = {key: avg_cumulative_rewards[key] for key in avg_cumulative_rewards.keys() if len(key) == k}
                chosen_arms = set(max(avg_cumulative_rewards_k.items(), key=operator.itemgetter(1))[0])
                print(chosen_arms) 
               
            counts[tuple(chosen_arms)] = counts[tuple(chosen_arms)] + 1             
            reward_chosen_arms = reward(list(chosen_arms))
            avg_cumulative_rewards[tuple(chosen_arms)] = avg_cumulative_rewards[tuple(chosen_arms)] \
                + div( reward_chosen_arms - avg_cumulative_rewards[tuple(chosen_arms)],counts[tuple(chosen_arms)])
                
            best_seed_sets_adgr.append(chosen_arms)
            obs_influences_adgr.append(reward_chosen_arms)
        
        avg_cumulative_rewards_k = {key: avg_cumulative_rewards[key] for key in avg_cumulative_rewards.keys() if len(key) == k}
        accept_set = set(max(avg_cumulative_rewards_k.items(), key=operator.itemgetter(1))[0])
        
        for arm in accept_set:
            if arm in A:
                A.remove(arm)
    print(accept_set)
    
    expPlusSomeTime = M(N,k)*num_samples + .01*(num_times - M(N,k)*num_samples)            
    for t in range(M(N,k)*num_samples,T):
        if t <= expPlusSomeTime:
            best_seed_sets_adgr.append(accept_set)
            obs_influences_adgr.append(reward(list(accept_set)))
        else:
            obs_influences_adgr.append(random.choice(obs_influences_adgr[M(N,k)*num_samples:]))
                
    return best_seed_sets_adgr, obs_influences_adgr

#"Testing"
#if __name__ == '__main__':
#    import networkx as nx
#    
#    network = nx.florentine_families_graph()
#    
#    "Converting the subgraph to a directed graph"
#    network = network.to_directed()
#    
#    "Relabeling the nodes as positive integers viz. 1,2,..."
#    network = nx.convert_node_labels_to_integers(network,first_label=1)
#    
#    x, y = adgr1_im(network, 2, 'independent_cascade', 1000, 10, 1)
