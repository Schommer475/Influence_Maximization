#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 16:49:45 2021

@author: niegu
"""

"Importing necessary modules"
from Utilities.influence import influence
import numpy as np
import os as os; os.getcwd()
import random
import copy
import networkx as nx
from Utilities.weighted_network import weighted_network
from Utilities.global_names import resources, facebook_network, communities, adaptive_temp
import pickle

def ucbgr_im(network, seed_set_size, diffusion_model, num_times, stage_horizon):
        
    np.random.seed(int(random.uniform(0, 1000000)))
    
    """
    Greedy UCB
    """
    "reward/influence function"
    def reward(arms_list):
        return influence(network, arms_list, diffusion_model, spontaneous_prob=[])
    
    "reset after each stage"
    def reset(k):
        # estimation for each action
        q_estimation = np.zeros(k)
        # # of chosen times for each action
        action_count = np.zeros(k)
        return q_estimation, action_count
    
    "Next action based on UCB1"
    def best_action(q_estimation, action_count, time):
        UCB_estimation = q_estimation + np.sqrt(2*np.log(time + 1) / (action_count + 1e-5))
        q_best = np.max(UCB_estimation)
        return np.random.choice(np.where(UCB_estimation == q_best)[0])
        
    N = len(network.nodes)
    K = seed_set_size
    T = num_times
    #random.shuffle(A)
    
    best_seed_sets_ucbgr = []
    obs_influences_ucbgr = []
    accept_set = []
    tbd_set = sorted(list(network.nodes()-accept_set))
    
    for k in range(K):
        q_estimation, action_count = reset(N-k)
        for t in range(stage_horizon):
            acc = copy.copy(accept_set)
            chosen_arm_index = best_action(q_estimation, action_count, t)
            #print(chosen_arm_index)
            
            action_count[chosen_arm_index] += 1
            #update action count
            
            acc.append(tbd_set[chosen_arm_index])
            reward_chosen_arms = reward(acc)
            
            nn = action_count[chosen_arm_index]
            
            q_estimation[chosen_arm_index] = q_estimation[chosen_arm_index]*(nn-1)/nn \
            + reward_chosen_arms/nn
            #update q_estimation
            
            best_seed_sets_ucbgr.append(set(acc))
            obs_influences_ucbgr.append(reward_chosen_arms)
            
            #print(acc)
            
        #new_acc = np.max(UCB_estimation)
        new_acc_q = np.max(q_estimation)
        new_accept_index = np.random.choice(np.where(q_estimation == new_acc_q)[0])
        accept_set.append(tbd_set[new_accept_index])
        accept_set = sorted(accept_set)
        del tbd_set[new_accept_index]
        
    print(accept_set)
    
    opt_inf = 0
    
    #Remaining time        
    for t in range((k+1)*stage_horizon, T):
        best_seed_sets_ucbgr.append(set(accept_set))
        infl = reward(accept_set)
        obs_influences_ucbgr.append(infl)
        opt_inf += infl
        
    print(opt_inf/(T-(k+1)*stage_horizon))
        
    return best_seed_sets_ucbgr, obs_influences_ucbgr

if __name__ == '__main__':
    
    """----------------------------------"""
    """READING/INTIALIZING THE NETWORK"""
    """Working with the Facebook network """
    "Reading the Facebook network from file"
    facebook_path = os.path.join(resources, facebook_network)
    network = nx.read_edgelist(facebook_path,create_using=nx.DiGraph(), nodetype = int)
    
    "Reading communities"
    communities_path = os.path.join(resources, communities)
    with open(communities_path, 'rb') as f:
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
    
    output_dir = adaptive_temp
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    name_id = '_fb4_ucbgr_16'
    output_dir = os.path.join(output_dir, "results" + name_id)
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    for i in range(5):
        rand_id = ''
        for j in range(8):
            rand_id += str(random.randint(0,9))
            
        best_seed_sets, obs_influences = ucbgr_im(network,16,"independent_cascade",100000,4000)
        
        results = {'rand_id':rand_id, 'best_seed_sets':best_seed_sets,'obs_influences':obs_influences}
        
        fstr = os.path.join(output_dir,'output_%s.pkl'%(rand_id))
        with open(fstr,'wb') as f:
            pickle.dump(results, f)
     
    #TODO find out if this is ever used
    '''
    with open('./results_fb4_ucbgr/output_ucbgr__1.00__16__10__100000__4000__27579598.pkl', 'rb') as f:
        df = pickle.load(f)
    '''

    
