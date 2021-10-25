#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 30 18:51:55 2020

@author: root
"""
import os
import pickle
from matplotlib import pyplot as plt
import numpy as np

name_id = '_fb4'
seed_set_sizes = [2,4,8]

"reading existing influences dictionary"
filename = 'results'+name_id+os.sep+'collate'+os.sep+'exp_influences_dict.pkl'
with open(filename, 'rb') as f:
    influences_dict = pickle.load(f)

influences = {}    
for seed_set_size in seed_set_sizes:
    influences[seed_set_size] = []
    for key in influences_dict.keys():
        if len(key) == seed_set_size:
            influences[seed_set_size].append(influences_dict[key])
    print(len(influences[seed_set_size]))
    f = plt.figure()
    plt.title('K='+str(seed_set_size))
    plt.plot(sorted(influences[seed_set_size]))
    plt.xlabel('seed set no.')
    plt.ylabel('expected influence')
    plt.grid()
    plt.axhline(y=np.mean(np.array(influences[seed_set_size])),linestyle='--')
    plt.savefig('results'+name_id+os.sep+'collate'+os.sep+'exp_influence_'+str(seed_set_size)+'.eps')
    plt.savefig('results'+name_id+os.sep+'collate'+os.sep+'exp_influence_'+str(seed_set_size)+'.jpg')