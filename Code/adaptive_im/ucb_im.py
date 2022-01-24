#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 18 02:23:56 2019

@author: abhishek.umrawal
"""

"Importing necessary modules"
from influence import influence
#from true_influence import true_influence
import numpy as np
import time as time
import os as os; os.getcwd()
import copy
import random


def ucb_im(network, seed_set_size, diffusion_model, num_times):
        
    np.random.seed(int(random.uniform(0, 1000000)))
    
    """
    UCB
    """
    def generate_actions(N, K):
        #import copy
        actions = []
        def printCombination(arr, n, r): 
            data = [0]*r; 
            combinationUtil(arr, data, 0, n - 1, 0, r); 

        def combinationUtil(arr, data, start, end, index, r): 
            if (index == r): 
                #print(data, end = "\n"); 
                act = copy.deepcopy(data)
                actions.append(act)
                return; 

            i = start; 
            while(i <= end and end - i + 1 >= r - index): 
                data[index] = arr[i]; 
                combinationUtil(arr, data, i + 1, end, index + 1, r); 
                i += 1; 

        # Driver Code 
        arr = np.arange(N)+1; 
        r = K; 
        n = len(arr); 
        printCombination(arr, n, r); 
        np.random.shuffle(actions)
        return actions

    
    "SORT"
    seed_sets_list = []
    
    def inf_function(seeds):
        return influence(network,seeds.tolist(),diffusion_model,spontaneous_prob=[])
    
    
    def play_arms(arm_list, inf_function):
        reward = inf_function(arm_list)
        a_list = copy.deepcopy(arm_list)
        seed_sets_list.append(a_list)
        #print(reward)
        return reward/len(network.nodes)
    
    
    def eliminate_arms_opt(action_list, precision, remaining_time, inf_function):
        round_r = 1
        consumed_time = 0
        all_sorted = 0

        reward_t = np.zeros(int(remaining_time+1))
        reward_t[0] = 0

        total_actions = len(action_list)
        is_eliminated = np.zeros(total_actions)
        p_a_hat = np.zeros(total_actions)
        consumed_time_a = np.zeros(total_actions)

        delta_r = np.power(0.5, round_r)
        n_r = np.log(T*delta_r*delta_r)*np.power(2, 2*round_r)

        num_eliminated_actions = 0

        valid_actions = np.arange(0, total_actions).tolist()

        while( ( num_eliminated_actions < total_actions ) & ( consumed_time < remaining_time ) ):
            for a in valid_actions:
                if( ( consumed_time < remaining_time ) ):
                    current_arms = action_list[a]
                    #print(consumed_time, current_arms)
                    reward = play_arms(np.array(current_arms), inf_function)

                    p_a_hat[a] =  consumed_time_a[a]*p_a_hat[a] +reward
                    consumed_time_a[a] = consumed_time_a[a] + 1
                    p_a_hat[a] = p_a_hat[a]/consumed_time_a[a]

                    reward_t[consumed_time] = reward
                    consumed_time = consumed_time + 1


            UCB_a = p_a_hat + delta_r
            LCB_a = p_a_hat - delta_r

            best_action = np.argmax(LCB_a)

            for a in valid_actions:
                if( ( UCB_a[a] < LCB_a[best_action]) ):
                    valid_actions.remove(a)
                    #print(len(valid_actions))
                    num_eliminated_actions = num_eliminated_actions +1

            if(max(consumed_time_a) >= n_r):
                round_r = round_r+1
                delta_r = np.power(0.5, round_r)
                n_r = np.log(T*delta_r*delta_r)*np.power(2, 2*round_r)
                
            if ( delta_r < precision ):
                break

        current_arms = action_list[np.argmax(p_a_hat)]
        while(consumed_time < remaining_time):
            # for a in valid_actions:
            reward = play_arms(np.array(current_arms), inf_function)

            p_a_hat[a] =  consumed_time_a[a]*p_a_hat[a] +reward
            consumed_time_a[a] = consumed_time_a[a] + 1
            p_a_hat[a] = p_a_hat[a]/consumed_time_a[a]

            if(consumed_time + 1 < len(reward_t)):
                reward_t[consumed_time] = reward
            consumed_time = consumed_time + 1

        return action_list[np.argmax(p_a_hat)], reward_t[0:consumed_time]
    
    
    def ucb_best_algo(T, N, K, inf_function):
        actions = generate_actions(N, K)
        num_actions = len(actions)
        precision = np.sqrt(num_actions*np.log(num_actions)/T)

        print("action space built")
        print("action space   : ", len(actions))
        print("Time available : ", T)

        best_seeds, reward_t = eliminate_arms_opt(actions, precision, T, inf_function)

        return best_seeds, reward_t
    
    
    "Printing Outputs"
    
    os.system('clear')
    #print("\n##################################################################################################\n")
    
    T = num_times
    N = len(network.nodes)
    ###############################################################################################
    diag_0 = False
    diag_1 = False
    
    K_list = [seed_set_size]
    run_time_sort = np.zeros(len(K_list))
    ###############################################################################################
    
    for K in K_list:
        lln = 0
    
        while(lln < 1):
            start_time_sort = time.time()
            best_seeds, rewards = ucb_best_algo(T, N, K, inf_function)
            end_time_sort = time.time()
    
            run_time_sort[K_list.index(K)] = lln*run_time_sort[K_list.index(K)] + (end_time_sort - start_time_sort)		
            lln = lln+1
    
    #print(len(rewards))
    rewards_final = []
    for i in range(0, len(rewards)):
        rewards_final.append(N*rewards[i])
    
    
    "Converting list of arrays of floats into a list of lists of integers"
    seed_sets_list = [list(arr) for arr in seed_sets_list]
    seed_sets_list = [[int(num) for num in l] for l in seed_sets_list]
    #seed_sets_list = [set(l) for l in seed_sets_list]
    
    
    best_seed_sets_cmab = seed_sets_list
    obs_influences_cmab = rewards_final
    
# =============================================================================    
#     "## Declaring an empty list of list of seed_sets and expected influences"      
#     exp_influences_dict = [[],[]] 
#     
#     "## Declaring an empty list of expected influences"
#     exp_influences_cmab = []
#    
#     "### Calculating the expected influences of all best seed sets in best_seed_sets_cd"
#     
#     for best_seed_set_cmab in best_seed_sets_cmab:
#         if (set(best_seed_set_cmab) in exp_influences_dict[0]): 
#             exp_influences_cmab.append(exp_influences_dict[1][exp_influences_dict[0].index(set(best_seed_set_cmab))]) 
#     else:
#         exp_influences_cmab.append(true_influence(network,best_seed_set_cd,diffusion_model,[]))
#         exp_influences_dict[0].append(set(best_seed_set_cmab))
#         exp_influences_dict[1].append(exp_influences_cmab[-1])
# =============================================================================
    
    return best_seed_sets_cmab, obs_influences_cmab
