#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:30:04 2019

2020-04-22 update to have separate copies of pvldb folder for each run (to avoid overwriting)


@author: abhishek.umrawal
"""

"Importing necessary modules"
from propagation_traces import propagation_traces
#from true_influence import true_influence
import numpy as np
import pandas as pd
import random
import os as os; os.getcwd()
import shutil

old_pvldb = '/home/aumrawal/jmlr2020-new/adaptive_im/pvldb12_code_release'
new_base = '/scratch/brown/aumrawal/jmlr2020-new/adaptive_im'

def ecd1_im(network,seed_set_size,epsilon,diffusion_model,num_times):
    
    np.random.seed(int(random.uniform(0, 1000000)))
    
    """
    To avoid overwritting, create a separate directory for each run.  label it with relevant information, and also give it a random id.  
    """
    streps = str(epsilon)
    streps = streps.replace('.','_')
    rand_id = ''
    for i in range(8):
        rand_id += str(random.randint(0,9))
    new_dir = 'ecd1--'+streps+'--'+str(seed_set_size)+'--'+str(num_times)+'--'+rand_id
    if new_dir not in os.listdir(new_base):
        os.mkdir(new_base+os.sep+new_dir)
    #now put a copy of pvdlb into it
    print('\n\nMoving directory:')
    print(old_pvldb)
    print('To:')
    print(new_base+os.sep+new_dir+os.sep+'pvldb12_code_release')
    shutil.copytree(old_pvldb,new_base+os.sep+new_dir+os.sep+'pvldb12_code_release')
    
    #move into the new directory
    os.chdir(new_base+os.sep+new_dir)
    
    
    
    """
    # Generating inputs for Goyal's software which are time independent viz.
        - IC.inf : the actual weighted diretced graph
        - graph.txt : the complete unweighted directed graph
    """
    
    "##Taking out weights from the weighted network"
    act_prob = []
    for edge in network.edges():
        act_prob.append(network[edge[0]][edge[1]]['act_prob'])
    
    "## Saving the weighted edge list as an inf file"
    edge_list=pd.DataFrame(list(network.edges),columns=['from','to'])
    IC=edge_list.copy(deep=True)
    IC['act_prob'] = act_prob
    IC.to_csv("./pvldb12_code_release/sample_dataset/IC.inf",sep=" ",index=False,header=True)
    
    "## Saving the complete unweighted directed graph as a text file"
    nodes = list(network.nodes)
    from_nodes = []
    to_nodes = []
    time = []
    for i in nodes:
        for j in nodes:
            if i !=j:    
                from_nodes.append(i)
                to_nodes.append(j)
                time.append(0)
    graph=pd.DataFrame()
    graph['from'] = from_nodes
    graph['to'] = to_nodes
    graph['time'] = time
    graph.to_csv("./pvldb12_code_release/sample_dataset/graph.txt",sep=" ",index=False,header=False)
              
    
    "## Removing the already existing actionslog.txt file as it is dynamically appended"
    if os.path.exists("./pvldb12_code_release/sample_dataset/actionslog.txt"):
      os.remove("./pvldb12_code_release/sample_dataset/actionslog.txt")
    
    "## Declaring empty output lists"
    times = []
    best_seed_sets_cd = []
    obs_influences_cd = []
    
    "## Generating the aforementioned inputs for the history until the current time"
    for time in range(num_times):
        
        print("ecd1_time = "+str(time))
        """
        ## Generating time dependent inputs for Goyal's software viz.
        - actionslog.txt : propagation traces for all diffusions so far
        - actions_in_training.txt : all actions taken so far
        - actions_in_testing.txt : empty file
        """
    
        "### Generating actionslog.txt"
        
        "### Declaring empty lists for the columns in actionslog.txt"
        user_id = []
        action_id = []
        timestamp = []
                    
        "#### Appending the time to times list"
        times.append(time+1) 
        
        "Seed set for diffusion"
        if (time == 0 or np.random.uniform() < epsilon): # and time < 1/num_times:
            best_seed_set_cd = random.sample(network.nodes,seed_set_size)
        
        "#### Appending the best seed set into a best seed sets list" 
        best_seed_sets_cd.append(best_seed_set_cd)            
        
        "### Finding the propagation traces"
        traces = propagation_traces(network,best_seed_set_cd,diffusion_model,spontaneous_prob=[])
        traces = traces[0:len(traces)]
        traces = [x for x in traces if x != []]
        
        user_id = [item for sublist in traces for item in sublist]
        action_id = list((time+1)*np.ones((len([item for sublist in traces for item in sublist]),), dtype=int))
        
        "### Appending the obs influence into an obs influences list"
        obs_influences_cd.append(len(user_id))
        
        
        for j in range(len(traces)):
            timestamp.append(list(j*np.ones(len(traces[j]),dtype=int)+1))
        timestamp = [item for sublist in timestamp for item in sublist]  
    
        actionslog = pd.DataFrame()
        actionslog['user_id'] = user_id
        actionslog['action_id'] = action_id
        actionslog['timestamp'] = timestamp
        actionslog.to_csv("./pvldb12_code_release/sample_dataset/actionslog.txt",mode ='a',sep=" ",index=False,header=False)

    
        "### Generating actions_in_training.txt"
        temp = pd.read_table("./pvldb12_code_release/sample_dataset/actionslog.txt", sep=' ',header=None)
        actions_in_training = pd.DataFrame()
        actions_in_training['actions_in_training']=list(set(temp[1]))
        actions_in_training.to_csv('./pvldb12_code_release/sample_dataset/actions_in_training.txt',sep=" ",index=False,header=False)
    
        "### Generating actions_in_testing.txt"
        actions_in_testing = pd.DataFrame()
        actions_in_testing['actions_in_testing']=[]
        actions_in_testing.to_csv('./pvldb12_code_release/sample_dataset/actions_in_testing.txt',sep=" ",index=False,header=False)    
        
        "### Running Goyal's software which is written in C and saving the outputs"
         
        "#### Modifying the input file config_maxinf_CD for the chosen seed set size"
        input_file = "pvldb12_code_release/config_files/config_maxinf_CD.txt"
        config_maxinf_CD = open(input_file).read().strip()
        edited_config_maxinf_CD = ' '.join(config_maxinf_CD.split(' ')[:-1] + [str(seed_set_size)])
        with open(input_file, "w") as f:
            f.write(edited_config_maxinf_CD)
            f.write('\n')
        
        "#### Changing directory to the Goyal's software folder, compiling the C codes by doing make and then coming back"
        os.chdir("pvldb12_code_release")
        os.system("make")
        os.chdir("..")
        
        "##### Input greneration phase"
        os.system("./pvldb12_code_release/InfluenceModels -c pvldb12_code_release/config_files/config_training_scan1.txt")
        os.system("./pvldb12_code_release/InfluenceModels -c pvldb12_code_release/config_files/config_training_scan2.txt")
        
        "#### Best seed set selection phase"
        os.system("./pvldb12_code_release/InfluenceModels -c pvldb12_code_release/config_files/config_maxinf_CD.txt")
        #os.system("./pvldb12_code_release/InfluenceModels -c pvldb12_code_release/config_files/config_maxinf_CD.txt")
        #os.system("./pvldb12_code_release/InfluenceModels -c pvldb12_code_release/config_files/config_true_spread.txt")
    
        "#### Output filename for best seed set"
        out_filename = os.path.join("pvldb12_code_release/sample_dataset/maxinf_CD", "PCCov_0_0.001.txt")
        
        "#### Getting the best seed set"
        best_seed_set_cd = [x.split(' ')[0] for x in open(out_filename).readlines()]
        
        best_seed_set_cd = [int(x) for x in best_seed_set_cd]
        
# =============================================================================
#         "#### Output filename for observed true influence"
#         out_filename1 = os.path.join("pvldb12_code_release/sample_dataset/maxinf_CD", "PCCov_0_0.001.txt_PCCov.txt")
#         
#         "### Getting the observed true influence of the best seed set"
#         obs_inluence_cd = [float(x) for x in [x.split(' ')[3] for x in open(out_filename1).readlines()]][1]
#         
# =============================================================================
    
        #best_seed_sets_cd.append(set(best_seed_set_cd))
        #unique_best_seed_sets_cd = [list(x) for x in set(tuple(x) for x in best_seed_sets_cd)]
                
# =============================================================================    
#     "## Declaring an empty list of list of seed_sets and expected influences"      
#     exp_influences_dict = [[],[]] 
#     
#     "## Declaring an empty list of expected influences"
#     exp_influences_cd = []
#    
#     "### Calculating the expected influences of all best seed sets in best_seed_sets_cd"
#     
#     for best_seed_set_cd in best_seed_sets_cd:
#         if (set(best_seed_set_cd) in exp_influences_dict[0]): 
#             exp_influences_cd.append(exp_influences_dict[1][exp_influences_dict[0].index(set(best_seed_set_cd))]) 
#     else:
#         exp_influences_cd.append(true_influence(network,best_seed_set_cd,diffusion_model,[]))
#         exp_influences_dict[0].append(set(best_seed_set_cd))
#         exp_influences_dict[1].append(exp_influences_cd[-1])
# =============================================================================`    
        
    return best_seed_sets_cd, obs_influences_cd