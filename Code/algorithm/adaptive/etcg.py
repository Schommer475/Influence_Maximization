# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 18:41:32 2022

@author: Tim Schommer
"""
from algorithm.algorithm import Algorithm
from application.application import Application
from parameters.parameterization_classes import ParamSet
import math
import numpy as np
import pickle

class Etcg(Algorithm):
    def __init__(self, data):
        self.data = data
        self.K = data.get("seed_set_size")
        self.T = data.get("time_horizon")
    
        
    def _reward(self, app, choices):
        return app.getReward(choices)
    
    def _calcM(self, N):
        T = self.T
        K = self.K
        numerator = T*math.sqrt(2*math.log(T))
        denominator = N+2*N*K*math.sqrt(2*math.log(T))
        quotient = numerator / denominator
        after_power = quotient**(2/3)
        m = math.floor(after_power)
        return m
    
    def refresh(self):
        ...
    
    def run(self, app: Application, pset: ParamSet, timestamp:str, randId:str):
        N = app.getOptionCount()
        
        m = self._calcM(N)
        
        selected_action_etcg = []
        obs_influences_etcg = []
        accept_set = []
        tbd_set = app.listOptions()
        time_step = 0 #time step counter
        
        for k in range(self.K):
            tbd_set_rewards = [0]*len(tbd_set)
            for i in range(len(tbd_set)):
                chosen_arms = accept_set+[tbd_set[i]]
                for count in range(m):
                    reward_chosen_arms = self._reward(app, chosen_arms)
                    tbd_set_rewards[i] += reward_chosen_arms
                    
                    selected_action_etcg.append(chosen_arms)
                    obs_influences_etcg.append(reward_chosen_arms)
                    time_step += 1
                    
                tbd_set_rewards[i] = tbd_set_rewards[i]/m
                
            new_acc_reward = np.max(tbd_set_rewards)
            tmp_set_rewards = np.array(tbd_set_rewards)
            new_accept_index = np.random.choice(np.where(tmp_set_rewards == new_acc_reward)[0])
            best_arm = tbd_set[new_accept_index]
            
            accept_set.append(best_arm)
            tbd_set.remove(best_arm)
            
        output = {"accept_set":accept_set}
        opt_inf = 0
        
        #Remaining time        
        for t in range(time_step, self.T):
            selected_action_etcg.append(accept_set)
            infl = self._reward(app, accept_set)
            obs_influences_etcg.append(infl)
            opt_inf += infl
            
        output["avg_opt_inf"] = opt_inf / (self.T - time_step)
        
        path = pset.getPath(timestamp, randId)
        fullpath = path + "optimalInfo.pkl"
        
        with open(fullpath, "wb") as f:
            pickle.dump(output, f)
            
        ret = dict()
        ret["best_seed_sets"] = selected_action_etcg
        ret["rewards"] = obs_influences_etcg
        return ret
        

def createInstance(data):
    return Etcg(data)