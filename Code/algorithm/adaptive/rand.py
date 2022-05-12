# -*- coding: utf-8 -*-
"""
Created on Thu May 12 11:26:59 2022

@author: Tim Schommer
"""

from algorithm.algorithm import Algorithm
from application.application import Application
from parameterization.parameterization_classes import ParamSet
import random

class Rand(Algorithm):
    def __init__(self, data):
        self.data = data
        self.K = data.get("seed_set_size")
        self.T = data.get("time_horizon")
        
        
        
    def run(self, app: Application, pset: ParamSet, timestamp:str, randId:str):
        "## Declaring empty output lists"
        best_seed_sets_rn = []
        obs_influences_rn = []
        
        options = app.listOptions()
        
        "## Generating the aforementioned inputs for the history until the current time"
        for time in range(self.T):
    
            "### Using a random seed set as the best seed set"
            best_seed_set_rn = random.sample(options,self.K)
    
            "### Appending the best seed set into a best seed sets list" 
            best_seed_sets_rn.append(best_seed_set_rn)  
    
            "### Appending the influence of the chosen seed set to the obs ifluences list" 
            obs_influences_rn.append(app.getReward(best_seed_set_rn))           

    
        return {"best_seed_sets":best_seed_sets_rn, "rewards":obs_influences_rn}
        
    def refresh(self):
        ...
        
        
def createInstance(params):
    return Rand(params)