
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
import networkx as nx
from weighted_network import weighted_network

def adgr2_im(network, seed_set_size, diffusion_model, num_times, num_samples, epsilon):
    
    
    network = nx.karate_club_graph()
    network = network.to_directed()
    network = nx.convert_node_labels_to_integers(network,first_label=1)
    
    network = weighted_network(network,'wc')  
    seed_set_size = 4
    diffusion_model = 'independent_cascade'
    num_times = 10000
    num_samples = 30
    epsilon = 1
    
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
    
    k = 1
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
    
    phase1_arms_order = [item[0][0] for item in sorted(avg_cumulative_rewards.items(), key=lambda item: item[1], reverse=True)]
    #phase1_rewards_order = [item[1] for item in sorted(avg_cumulative_rewards.items(), key=lambda item: item[1], reverse=True)]
                   
    for k in range(2,K+1):
        k = 2
        
        arm = [item for item in phase1_arms_order if item not in accept_set][0]
        arm_next_in_order = [item for item in phase1_arms_order if item not in accept_set][1]
    
        chosen_arms = accept_set.union({arm})

        for t in range(0,num_samples):
            counts[tuple(chosen_arms)] = counts[tuple(chosen_arms)] + 1             
            reward_chosen_arms = reward(list(chosen_arms))
            avg_cumulative_rewards[tuple(chosen_arms)] = avg_cumulative_rewards[tuple(chosen_arms)] \
                + div( reward_chosen_arms - avg_cumulative_rewards[tuple(chosen_arms)],counts[tuple(chosen_arms)])
        
            best_seed_sets_adgr.append(chosen_arms)
            obs_influences_adgr.append(reward_chosen_arms)
            
        sum_ind_rewards_for_arms_in_accept_set = sum([avg_cumulative_rewards[tuple({arm})] for arm in accept_set])  
            
        if avg_cumulative_rewards[tuple(chosen_arms)] > sum_ind_rewards_for_arms_in_accept_set + avg_cumulative_rewards[tuple({arm_next_in_order})]:
            print(True)
            break
        else: 
            phase1_arms_order.remove(arm)
                
            
        

         
          
         
   
        #for t in range(M(N,k-1)*num_samples, M(N,k-1)*num_samples + num_samples):           
         
    
    

    
    expPlusSomeTime = M(N,k)*num_samples + .01*(num_times - M(N,k)*num_samples)            
    for t in range(M(N,k)*num_samples,T):
        if t <= expPlusSomeTime:
            best_seed_sets_adgr.append(accept_set)
            obs_influences_adgr.append(reward(list(accept_set)))
        else:
            obs_influences_adgr.append(random.choice(obs_influences_adgr[M(N,k)*num_samples:]))
                
    from matplotlib import pyplot as plt  
    print(len(obs_influences_adgr))
    plt.plot(obs_influences_adgr)
    
    return best_seed_sets_adgr, obs_influences_adgr


