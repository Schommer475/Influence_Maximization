#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  1 06:58:23 2020

@author: root
"""

import pickle

"File to look up expected influences from"
filename = 'infl_vals_10000.pkl'

with open(filename, 'rb') as f:
    exp_influences_dict = pickle.load(f)          

"Finding optimal solution"
seed_set_sizes = [2,4,8,16,32]
for seed_set_size in seed_set_sizes:
    
    temp_dict = {}
    for key in exp_influences_dict:
        if len(key) == seed_set_size:
            temp_dict[key] = exp_influences_dict[key]
    
    inverse_temp_dict = [(value, key) for key, value in temp_dict.items()]
    print(max(inverse_temp_dict)[1])
    print(max(inverse_temp_dict)[0])