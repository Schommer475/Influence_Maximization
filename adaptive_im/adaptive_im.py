#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:01:00 2019

@author: abhishek.umrawal
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 19:17:14 2019

@author: abhishek.umrawal
"""

"Importing necessary modules"
from weighted_network import weighted_network
from adgr1_im import adgr1_im
#from adgr2_im import adgr2_im
from ucbgr_im import ucbgr_im
import IMLinUCB
from dart_im import dart_im
from cmab_im import cmab_im
#from csar_im import csar_im
from ecd1_im import ecd1_im
from ecd2_im import ecd2_im
from ucb_im import ucb_im
from rand_im import rand_im
import random
import pickle
import networkx as nx
import os; os.getcwd()

"Input and output directories (NEED to be defined in main_multi_run as well)"
#input_dir = '/scratch/brown/aumrawal/jmlr2020-new/adaptive_im'
#output_dir = '/home/aumrawal/jmlr2020-new/adaptive_im'

input_dir = os.getcwd()
output_dir = '/scratch/brown/nieg/'

if not os.path.exists(input_dir):
    os.mkdir(input_dir)

def adaptive_im(inpt):
    network, weighting_scheme, seed_set_size, epsilon, \
    diffusion_model, num_times, num_samples, stage_horizon, algorithm, name_id, df_feats = inpt
    
    "## Adding weights to the unweighted network"
    network = weighted_network(network,method = weighting_scheme)
    
    "Random id for a particular run"
    rand_id = ''
    for i in range(8):
        rand_id += str(random.randint(0,9))
    print('I am running with seed set size k=%i for alg = %s with num_samples = %i, stage_horizon=%i and id=%s'%(seed_set_size,algorithm,num_samples,stage_horizon,rand_id))
    
    "Calling the required algorithm"
    
    if (algorithm == "adgr1"):
        best_seed_sets, obs_influences = adgr1_im(network,seed_set_size,diffusion_model,num_times,num_samples,epsilon)
    
    #elif (algorithm == "adgr2"):
    #    best_seed_sets, obs_influences = adgr2_im(network,seed_set_size,diffusion_model,num_times,num_samples,epsilon)
    
    elif (algorithm == "ucbgr"):
        best_seed_sets, obs_influences = ucbgr_im(network,seed_set_size,diffusion_model,num_times,stage_horizon)  
        
    #elif (algorithm == "csar"):
        #best_seed_sets, obs_influences = csar_im(network,seed_set_size,diffusion_model,num_times)
        
    elif (algorithm == "dart"):
        best_seed_sets, obs_influences = dart_im(network,seed_set_size,diffusion_model,num_times)
    
    elif (algorithm == "cmab"):
        best_seed_sets, obs_influences = cmab_im(network,seed_set_size,diffusion_model,num_times)
    
    elif (algorithm == "ecd1"):
        best_seed_sets, obs_influences = ecd1_im(network,seed_set_size,epsilon,diffusion_model,num_times)    
    
    elif (algorithm == "ecd2"):
        best_seed_sets, obs_influences = ecd2_im(network,seed_set_size,epsilon,diffusion_model,num_times) 
        
    elif (algorithm == "ucb"):
        best_seed_sets, obs_influences = ucb_im(network,seed_set_size,diffusion_model,num_times)  
    
    elif (algorithm == "rand"):
        best_seed_sets, obs_influences = rand_im(network,seed_set_size,diffusion_model,num_times)      
    
    elif (algorithm == "imlinucb"):
        dic = IMLinUCB.imlinucb_node2vec(G=network, df_feats=df_feats, num_inf=seed_set_size, num_repeats=num_times)
        best_seed_sets = dic["seed_sets"]
        obs_influences = dic["rewards"]
    
#    time.sleep(1)
    results = {'weighting_scheme':weighting_scheme, 'seed_set_size':seed_set_size, \
               'epsilon':epsilon, 'diffusion_model':diffusion_model,'num_times':num_times,'stage_horizon':stage_horizon,\
               'algorithm':algorithm,'rand_id':rand_id, 'best_seed_sets':best_seed_sets,\
               'obs_influences':obs_influences,'num_samples':num_samples}
    os.chdir(output_dir)
    print(os.getcwd())
    if not os.path.exists('results'+name_id):
        os.mkdir('results'+name_id)
    fstr = 'results'+name_id+os.sep+'output_%s__%0.2f__%i__%i__%i__%i__%s.pkl'%(algorithm,epsilon,seed_set_size,num_samples,num_times,stage_horizon,rand_id)
    with open(fstr,'wb') as f:
        pickle.dump(results, f)

    return