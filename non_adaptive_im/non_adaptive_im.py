#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:01:00 2019

@author: abhishek.umrawal
"""

"importing necessary modules"
from weighted_network import weighted_network
from degree_im import degree_im
from wdegree_im import wdegree_im
from greedy_im import greedy_im
import pickle
import os as os; os.getcwd()

def non_adaptive_im(inpt):
    
    network, weighting_scheme, seed_set_size, diffusion_model, algorithm, n_sim, num_procs, name_id = inpt
    
    "## adding weights to the unweighted network"
    network = weighted_network(network,method = weighting_scheme)
    
    if (algorithm == "degree"):
        best_seed_set, exp_influence = degree_im(network,seed_set_size,diffusion_model,[],n_sim)
    
    elif (algorithm == "wdegree"):
        best_seed_set, exp_influence = wdegree_im(network,seed_set_size,diffusion_model,[],n_sim)     
    
    elif (algorithm == "greedy"):
        best_seed_set, exp_influence = greedy_im(network,seed_set_size,diffusion_model,[],n_sim,num_procs)  
            
    results = {'weighting_scheme':weighting_scheme, 'seed_set_size':seed_set_size, \
               'diffusion_model':diffusion_model, 'algorithm':algorithm, \
                   'best_seed_set':best_seed_set, 'name_id':name_id, 'exp_influence':exp_influence}
        
    #print(os.getcwd())
    if not os.path.exists('results'+name_id):
        os.mkdir('results'+name_id)
    fstr = 'results'+name_id+os.sep+'output_%s__%i__.pkl'%(algorithm,seed_set_size)
    with open(fstr,'wb') as f:
        pickle.dump(results, f)
        
    return 