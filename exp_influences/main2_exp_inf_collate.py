#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 29 19:19:43 2020

@author: root
"""
import pickle
import os       

name_id = '_fl'

#if not os.path.exists('results'+name_id+os.sep+'collate'):
#    os.makedirs('results'+name_id+os.sep+'collate')

"Looking up and collating in a single file"    
exp_influences_dict = {}        
print(len(os.listdir('results'+name_id+os.sep+'compute')))         
for i,filename in enumerate(os.listdir('results'+name_id+os.sep+'compute')):  
    filename_with_path = 'results'+name_id+os.sep+'compute'+os.sep+filename
    # print(filename)
    try:
        if not os.path.isdir(filename_with_path) and not filename.startswith('.') and not filename.startswith('Icon'):        
            with open(filename_with_path, 'rb') as f:
                results = pickle.load(f)
        exp_influences_dict['diffusion_model'] = results['diffusion_model']
        exp_influences_dict['n_sim'] = results['n_sim']
        exp_influences_dict['spontaneous_prob']  = results['spontaneous_prob']
        exp_influences_dict['name_id'] = results['name_id']       
                    
        exp_influences_dict.update(results['exp_influences_dict']) 
    except:
        pass
       
"Dumping the expected influences dictionary in a single pickle file"
fstr = 'results'+name_id+os.sep+'exp_influences_dict.pkl'
with open(fstr,'wb') as f:
    pickle.dump(exp_influences_dict, f)