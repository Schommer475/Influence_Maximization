# -*- coding: utf-8 -*-
"""
Created on Thu May 12 11:34:44 2022

@author: Tim Schommer
"""

from algorithm.algorithm import Algorithm
from application.application import Application
from parameterization.parameterization_classes import ParamSet
from Utilities.program_vars import algorithms_index
import numpy as np
import copy

class UCBGR(Algorithm):
    def __init__(self, data):
        self.data = data
        self.K = data.get("seed_set_size")
        self.T = data.get("time_horizon")
        
        
        
    def run(self, app: Application, pset: ParamSet, timestamp:str, randId:str):
        N = app.getOptionCount()
        K = self.K
        T = self.T
        #random.shuffle(A)
        
        best_seed_sets_ucbgr = []
        obs_influences_ucbgr = []
        accept_set = []
        tbd_set = sorted(list(app.listOptions()-accept_set))
        
        for k in range(K):
            q_estimation, action_count = self.reset(N-k)
            for t in range(pset.get(algorithms_index, "stage_horizon")):
                acc = copy.copy(accept_set)
                chosen_arm_index = self.best_action(q_estimation, action_count, t)
                #print(chosen_arm_index)
                
                action_count[chosen_arm_index] += 1
                #update action count
                
                acc.append(tbd_set[chosen_arm_index])
                reward_chosen_arms = app.getReward(acc)
                
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
        for t in range((k+1)*pset.get(algorithms_index, "stage_horizon"), T):
            best_seed_sets_ucbgr.append(set(accept_set))
            infl = app.getReward(accept_set)
            obs_influences_ucbgr.append(infl)
            opt_inf += infl
            
        print(opt_inf/(T-(k+1)*pset.get(algorithms_index, "stage_horizon")))
            
        return {"best_seed_sets":best_seed_sets_ucbgr, "rewards":obs_influences_ucbgr}
        
    def refresh(self):
        ...
        
    def reset(self, k):
        # estimation for each action
        q_estimation = np.zeros(k)
        # # of chosen times for each action
        action_count = np.zeros(k)
        return q_estimation, action_count
    
    def best_action(self, q_estimation, action_count, time):
        UCB_estimation = q_estimation + np.sqrt(2*np.log(time + 1) / (action_count + 1e-5))
        q_best = np.max(UCB_estimation)
        return np.random.choice(np.where(UCB_estimation == q_best)[0])
        
        
def createInstance(params):
    return UCBGR(params)