#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 00:34:29 2020

@author: abhishek.umrawal
"""

for k in range(2,K+1):
    k = 2
    arm = [item for item in phase1_arms_order if item not in accept_set][0]
    arm_next_in_order = [item for item in phase1_arms_order if item not in accept_set][1]
    for t in range(M(N,k-1)*num_samples, M(N,k-1)*num_samples + num_samples):          
        chosen_arms = accept_set.union({arm})
        counts[tuple(chosen_arms)] = counts[tuple(chosen_arms)] + 1             
        reward_chosen_arms = reward(list(chosen_arms))
        avg_cumulative_rewards[tuple(chosen_arms)] = avg_cumulative_rewards[tuple(chosen_arms)] \
            + div( reward_chosen_arms - avg_cumulative_rewards[tuple(chosen_arms)],counts[tuple(chosen_arms)])
    
    sum_ind_rewards_for_arms_in_accept_set = sum([avg_cumulative_rewards[tuple({arm})] for arm in accept_set])  
    
    if avg_cumulative_rewards[tuple(chosen_arms)] > sum_ind_rewards_for_arms_in_accept_set + avg_cumulative_rewards[tuple({arm_next_in_order})]:
        print(True)