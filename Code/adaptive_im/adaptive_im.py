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
from Utilities.weighted_network import weighted_network
from Utilities.global_names import adaptive_temp
from adaptive_im.adgr1_im import adgr1_im
#from adaptive_im.adgr2_im import adgr2_im
from adaptive_im.ucbgr_im import ucbgr_im
import adaptive_im.IMLinUCB as IMLinUCB
from adaptive_im.dart_im import dart_im
from adaptive_im.cmab_im import cmab_im
from adaptive_im.ucb_im import ucb_im
from adaptive_im.rand_im import rand_im
import random
import pickle
import networkx as nx
import os; os.getcwd()

"Input and output directories (NEED to be defined in main_multi_run as well)"
#input_dir = '/scratch/brown/aumrawal/jmlr2020-new/adaptive_im'
#output_dir = '/home/aumrawal/jmlr2020-new/adaptive_im'



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
        
    elif (algorithm == "dart"):
        best_seed_sets, obs_influences = dart_im(network,seed_set_size,diffusion_model,num_times)
    
    elif (algorithm == "cmab"):
        best_seed_sets, obs_influences = cmab_im(network,seed_set_size,diffusion_model,num_times)
    
    elif (algorithm == "ucb"):
        best_seed_sets, obs_influences = ucb_im(network,seed_set_size,diffusion_model,num_times)  
    
    elif (algorithm == "rand"):
        best_seed_sets, obs_influences = rand_im(network,seed_set_size,diffusion_model,num_times)      
    
    elif (algorithm == "imlinucb"):
        temp_directory = os.path.join(adaptive_temp, "ImLinUCB_temp")
        dic = IMLinUCB.imlinucb_node2vec(G=network, df_feats=df_feats, num_inf=seed_set_size, 
                                         num_repeats=num_times,tempdir_name=temp_directory)
        best_seed_sets = dic["seed_sets"]
        obs_influences = dic["rewards"]
    
#    time.sleep(1)
    results = {'weighting_scheme':weighting_scheme, 'seed_set_size':seed_set_size, \
               'epsilon':epsilon, 'diffusion_model':diffusion_model,'num_times':num_times,'stage_horizon':stage_horizon,\
               'algorithm':algorithm,'rand_id':rand_id, 'best_seed_sets':best_seed_sets,\
               'obs_influences':obs_influences,'num_samples':num_samples}
    if not os.path.exists(adaptive_temp):
        os.mkdir(adaptive_temp)
        
    output_dir = os.path.join(adaptive_temp, 'results'+name_id)
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    fstr = os.path.join(output_dir,'output_%s__%0.2f__%i__%i__%i__%i__%s.pkl'%(algorithm,epsilon,seed_set_size,num_samples,num_times,stage_horizon,rand_id))
    with open(fstr,'wb') as f:
        pickle.dump(results, f)

    return
