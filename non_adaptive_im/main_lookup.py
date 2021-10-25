#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  1 05:28:39 2020

@author: abhishek.umrawal
"""

"importing necessary modules"
import os as os; os.getcwd()
import pickle
import numpy as np

name_id = '_fb4_new'

"ivestigating the chosen seed_set and  expected influence"

filenames = np.sort(os.listdir('results'+name_id))
#print(filenames)
for filename in [filenames[2]]: 
    print(filename)
    if not filename.startswith('.'):
    
        filename_with_path = 'results'+name_id+os.sep+filename
        filename_split = filename.split('__')
        
        if os.path.isdir(filename_with_path):
            continue
        
        with open(filename_with_path, 'rb') as f:
            obs_influences_dict = pickle.load(f)
        
        best_seed_set = obs_influences_dict['best_seed_set']
        obs_influence = obs_influences_dict['exp_influence']