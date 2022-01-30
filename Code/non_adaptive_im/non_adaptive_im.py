#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:01:00 2019

@author: abhishek.umrawal
"""

"importing necessary modules"
from Utilities.weighted_network import weighted_network
from non_adaptive_im.degree_im import degree_im
from non_adaptive_im.wdegree_im import wdegree_im
from non_adaptive_im.greedy_im import greedy_im
from Utilities.global_names import non_adaptive_temp
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
    output_dir = non_adaptive_temp
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    output_dir = os.path.join(output_dir, "results" + name_id)
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    fstr = os.path.join(output_dir,'output_%s__%i__.pkl'%(algorithm,seed_set_size))
    with open(fstr,'wb') as f:
        pickle.dump(results, f)
        
    return 
