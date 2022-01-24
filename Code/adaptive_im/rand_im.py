#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:30:04 2019

2020-04-22 update to have separate copies of pvldb folder for each run (to avoid overwriting)


@author: abhishek.umrawal
"""

"Importing necessary modules"
from influence import influence
import numpy as np
import random
import os as os; os.getcwd()

def rand_im(network,seed_set_size,diffusion_model,num_times):
    
    np.random.seed(int(random.uniform(0, 1000000)))
    
    "## Declaring empty output lists"
    best_seed_sets_rn = []
    obs_influences_rn = []
    
    "## Generating the aforementioned inputs for the history until the current time"
    for time in range(num_times):
        
#        if time in [int(np.floor(x)) for x in np.linspace(0,num_times,100)]:
#            print("random_time = "+str(time))

        "### Using a random seed set as the best seed set"
        best_seed_set_rn = random.sample(network.nodes,seed_set_size)

        "### Appending the best seed set into a best seed sets list" 
        best_seed_sets_rn.append(best_seed_set_rn)  

        "### Appending the influence of the chosen seed set to the obs ifluences list" 
        obs_influences_rn.append(influence(network, best_seed_set_rn,diffusion_model,spontaneous_prob=[]))           

    
    return best_seed_sets_rn, obs_influences_rn
