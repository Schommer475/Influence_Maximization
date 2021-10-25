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
#from matplotlib import pyplot as plt

name_id = '_fb4_new'

"ivestigating the chosen seed_sets and  expected influence"
best_seed_sets = []
obs_influences = []
#os.chdir('../adaptive_im')
filenames = np.sort(os.listdir('results'+name_id))
#print(filenames)
for filename in [filenames[1]]: 
    print(filename)
    if not filename.startswith('.'):
    
        filename_with_path = 'results'+name_id+os.sep+filename
        filename_split = filename.split('__')
        
        if os.path.isdir(filename_with_path):
            continue
        
        with open(filename_with_path, 'rb') as f:
            obs_influences_dict = pickle.load(f)
        
        best_seed_sets.append(obs_influences_dict['best_seed_sets'])
        obs_influences.append(obs_influences_dict['obs_influences'])

best_seed_sets = [item for sub_list in best_seed_sets for item in sub_list]
obs_influences = [item for sub_list in obs_influences for item in sub_list]

"bar plot of lengths"
lengths = [len(item) for item in best_seed_sets]
values,counts = [],[]
values = list(np.unique(lengths))
for value in values:
    counts.append(lengths.count(value)) 
#plt.figure(1)
#plt.bar(values,counts)

"histogram of obs influenecs"
counts,values = list(np.histogram(obs_influences))
#plt.figure(2)
#plt.bar(list(values[:-1]),list(counts))
