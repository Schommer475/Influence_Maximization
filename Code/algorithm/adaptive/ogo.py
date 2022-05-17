# -*- coding: utf-8 -*-
"""
Created on Thu May 12 10:47:31 2022

@author: Tim Schommer
"""

from algorithm.algorithm import Algorithm
from application.application import Application
from parameters.parameterization_classes import ParamSet
from Utilities.program_vars import joint_index
import numpy as np
import math
import random

class OGO(Algorithm):
    def __init__(self, params):
        self.params = params
        self.K = params.get("seed_set_size")
        self.T = params.get("time_horizon")
        
    def run(self, app: Application, pset: ParamSet, timestamp:str, randId:str):
        N = pset.get(joint_index, "N")
        K = self.K
        T = self.T
        options = app.listOptions()
        
        gamma = pset.get(joint_index, "gamma")
            
        #learning rate for WMR algorithm
        epsilon = pset.get(joint_index, "epsilon")
        
        selected_action_ogo = []
        obs_influences_ogo = []
        weights = np.array([[1 for i in range(N)] for j in range(K)], dtype='float')
        
        for i in range(T):
            #Explore with probability gamma
            if random.random() <= gamma:
                selected_action = []
                update_expert = random.randint(0,K-1)
                loss = np.array([[0 for i in range(N)] for j in range(K)], dtype='float')
                for j in range(update_expert):
                    prob = [number/sum(weights[j]) for number in weights[j]]
                    #sample 
                    while True:
                        a = np.random.choice(options, 1, p=prob)[0]
                        if a not in selected_action:
                            break
                    selected_action.append(a)
                
                explore_arm_index = np.random.choice([x for x in range(N) if options[x] not in selected_action], 1)[0]
                explore_arm = options[explore_arm_index]
                selected_action.append(explore_arm)
                
                selected_action_ogo.append(selected_action)
                explore_reward = app.getReward(selected_action)
                
                for p in range(K):
                    for q in range(N):
                        if p != update_expert:
                            loss[p][q] = 0
                        elif p == update_expert and explore_arm_index == q:
                            loss[p][q] = 0
                        else:
                            loss[p][q] = explore_reward
                        weights[p][q] *= math.exp(-epsilon*loss[p][q])
                
                obs_influences_ogo.append(explore_reward)
                
            else:
                selected_action = []
                for j in range(K):
                    prob = [number/sum(weights[j]) for number in weights[j]]
                    while True:
                        a = np.random.choice(options, 1, p=prob)[0]
                        if a not in selected_action:
                            break
                    selected_action.append(a)
                
                selected_action_ogo.append(selected_action)
                obs_influences_ogo.append(app.getReward(selected_action))
            
            
        return {"best_seed_sets":selected_action_ogo, "rewards":obs_influences_ogo}
        
    def refresh(self):
        ...
        

def createInstance(params):
    return OGO(params)