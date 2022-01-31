#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 21:49:19 2019

@author: abhishek.umrawal
"""
import pickle as pickle
import os as os
import numpy as np
import pandas as pd
from Utilities.global_names import non_adaptive_temp, adaptive_temp, \
    compilation_temp
#import matplotlib.pyplot as plt
#%matplotlib

"Ignore division by zero"
def div(n,d):
    return n/d if d else 0 

"Total historical average"
def tha(x):
    return list(np.divide(np.cumsum(x),np.cumsum([1]*len(x))))

"Moving average"
def ma(x,d=500):
    i = 0
    ma_x = []
    while i < len(x) - d + 1:
        ma_x.append(sum(x[i : i + d]) / d)
        i += 1
    return ma_x

def main():
    """--------------------------------"""
    "Inputs"
    seed_set_sizes =  ['16']         # ['2','4','8'] # list of seed set sizes
    algorithms = ['ucbgr']                  # ['adgr1','cmab','csar','dart','ecd2','ucb','rand'] #algorithms
    nested_na_algorithms = []       # ['degree','wdegree','greedy'] # non-adaptive algos with nested solutions
    epsilons = ['1.00']       # ['0.10','0.25','1.00']  # exploration parameter for ecd_im and adgr_im
    nums_samples = ['5']     # ['5','10','20','30'] # list of values of C for adgr, lower the C, lower the exploration
    stage_horizons = ['1000','2000','3000','4000']       # [100000] # stage horizon for the ucbgr algorithm
    name_id = '_fb4_16'                        # identifier to name the output folder as results_<name_id>
    aggregate = 'cumsum'                        # ['ma','cumsum'] # method for smoothing of the rewards over time horizon 
    num_samples = []
    """--------------------------------"""
    
    """Notes on Inputs"""
    # all inputs are in list format except name_id and aggregate
    # even numeric inputs are entered as STRINGS 
    # MAKE SURE to inlude the MAX budget in seed_set_sizes if nested_na_algorithms is non-empty
    # because for non_adaptive_im the output is a single file named output_<nested_na_algorithm>_<max_budget> for all seed set sizes 
    # LEAVE nested_na_algorithms as [] if the corresponding files aren't there in the results_<name_id> folder inside the non_adaptive_im folder
    
    try:
        filename = os.path.join(non_adaptive_temp,'results'+name_id,'optimal_im_res1.pkl')
        with open(filename, 'rb') as f:
            optimal_im_res=pickle.load(f)
    except:
        optimal_im_res = {}
        for seed_set_size in seed_set_sizes:
            optimal_im_res[int(seed_set_size)] = [[],0]
    
    "Averaging for adaptive methods"
    optimal_im_res = {}
    optimal_im_res[4] = [[],138.097]
    optimal_im_res[8] = [[],183.805]
    optimal_im_res[16] = [[],235.644]
    optimal_im_res[32] = [[],287.297]
    
    output_dict = {}
    for seed_set_size in seed_set_sizes:
        for algorithm in algorithms:
            for epsilon in epsilons:  
                for stage_horizon in stage_horizons:
                    for num_samples in nums_samples:
                        # all observed influences       
                        all_obs_influence = []
                        count = 0 
                        basepath = os.path.join(adaptive_temp,'results'+name_id)
                        for filename in os.listdir(basepath):
                            try:
                                filename_split = filename.split('__')
                                if (filename_split[0] == 'output_'+algorithm and filename_split[1] == epsilon and \
                                    filename_split[2] == seed_set_size and filename_split[5] == stage_horizon):
                                    #print(filename)
                                    count = count + 1
                                    filename_with_path = os.path.join(basepath,filename)
                                    with open(filename_with_path, 'rb') as f:
                                        all_influence_dict = pickle.load(f)
                                        all_obs_influence.append(all_influence_dict['obs_influences'])
                            except:
                                print(filename)
                                #os.remove('results_with_exp/'+os.sep+filename)
                        if count > 0:    
                            print(algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon+'__'+stage_horizon+'__'\
                                  +str(count))
                        
                        # all observed regrets
                        #print(optimal_im_res[int(seed_set_size)][1])
    #                    try:
    #                        opt_influence = [optimal_im_res[int(seed_set_size)][1]]*len(all_obs_influence[0])
    #                    except:
    #                        continue
                        
                        opt_influence = [optimal_im_res[int(seed_set_size)][1]]*len(all_obs_influence[0])
                            
                        all_obs_regret = []
                        for x in all_obs_influence:
                            all_obs_regret.append(np.array(opt_influence) - list(np.array(x)))
            
                        # all cumulative observed influences
                        all_cumsum_obs_influence = []
                        for x in all_obs_influence:
                            all_cumsum_obs_influence.append(list(np.cumsum(x)))
                        
                        # all cumulative observed regrets
                        all_cumsum_obs_regret = []
                        for x in all_obs_regret:
                            all_cumsum_obs_regret.append(list(np.cumsum(x)))
                            
                        if aggregate == 'ma':
            
                            # ma of average, minimum and maximum cumulative observed infleunce
                            #output_dict['avg_obs_influence_'+algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon] = [np.mean(x) for x in zip(*all_obs_influence)]
                            
                            output_dict['ma_avg_obs_influence_'+algorithm+'__'+seed_set_size+'__'+stage_horizon+'__'+epsilon] = ma([np.mean(x) for x in zip(*all_obs_influence)])
                            #output_dict['ma_avg_obs_influence_'+algorithm+'__'+seed_set_size+'__'+stage_horizon+'__'+epsilon] = ma([np.std(x) for x in zip(*all_obs_influence)])
                            #output_dict['ma_min_obs_influence_'+algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon] = ma([min(x) for x in zip(*all_obs_influence)])
                            #output_dict['ma_max_obs_influence_'+algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon] = ma([max(x) for x in zip(*all_obs_influence)])
                            
                            # average, minimum and maximum cumulative observed regret   
                            #output_dict['avg_obs_regret_'+algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon] = [np.mean(x) for x in zip(*all_obs_regret)]
                            
                            output_dict['ma_avg_obs_regret_'+algorithm+'__'+seed_set_size+'__'+stage_horizon+'__'+epsilon] = ma([np.mean(x) for x in zip(*all_obs_regret)])
                            #output_dict['ma_avg_obs_regret_'+algorithm+'__'+seed_set_size+'__'+stage_horizon+'__'+epsilon] = ma([np.std(x) for x in zip(*all_obs_regret)])
                            #output_dict['ma_min_obs_regret_'+algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon] = ma([min(x) for x in zip(*all_obs_regret)])
                            #output_dict['ma_max_obs_regret_'+algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon] = ma([max(x) for x in zip(*all_obs_regret)])
                        
                        elif aggregate == 'cumsum':
                            
                            output_dict['avg_cumsum_obs_influence_'+algorithm+'__'+seed_set_size+'__'+stage_horizon+'__'+epsilon] = [np.mean(x) for x in zip(*all_cumsum_obs_influence)]
                            #output_dict['avg_cumsum_obs_influence_'+algorithm+'__'+seed_set_size+'__'+stage_horizon+'__'+epsilon] = [np.std(x) for x in zip(*all_cumsum_obs_influence)]
                            #output_dict['min_cumsum_obs_influence_'+algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon] = [min(x) for x in zip(*all_cumsum_obs_influence)]
                            #output_dict['max_cumsum_obs_influence_'+algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon] = [max(x) for x in zip(*all_cumsum_obs_influence)]
                            
                            output_dict['avg_cumsum_obs_regret_'+algorithm+'__'+seed_set_size+'__'+stage_horizon+'__'+epsilon] = [np.mean(x) for x in zip(*all_cumsum_obs_regret)]
                            #output_dict['avg_cumsum_obs_regret_'+algorithm+'__'+seed_set_size+'__'+stage_horizon+'__'+epsilon] = [np.std(x) for x in zip(*all_cumsum_obs_regret)]
                            #output_dict['min_cumsum_obs_regret_'+algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon] = [min(x) for x in zip(*all_cumsum_obs_regret)]  
                            #output_dict['max_cumsum_obs_regret_'+algorithm+'__'+seed_set_size+'__'+num_samples+'__'+epsilon] = [max(x) for x in zip(*all_cumsum_obs_regret)]     
    
    "Looking up for nested non-adaptive methods"
    #na_output_dict={}
    #max_budget = max([int(x) for x in seed_set_sizes])
    #for algorithm in nested_na_algorithms:
    #    try:
    #        for filename in os.listdir('../non_adaptive_im/results'+str(name_id)):
    #            filename_split = filename.split('__')
    #            if (filename_split[0] == 'output_'+algorithm and filename_split[1] == str(max_budget)):
    #                print(algorithm+'__'+str(seed_set_size))
    #                filename_with_path = '../non_adaptive_im/results'+str(name_id)+os.sep+filename
    #                with open(filename_with_path, 'rb') as f:
    #                     exp_influence_dict = pickle.load(f)
    #        na_output_dict[algorithm] = exp_influence_dict['exp_influence']   
    #    except:
    #        pass
    #
    #max_key = max(output_dict, key= lambda x: len(set(output_dict[x])))    
    #for seed_set_size in [int(x) for x in seed_set_sizes]:
    #    for algorithm in nested_na_algorithms:
    #        
    #        try:
    #            opt_influence = optimal_im_res[int(seed_set_size)][1]
    #        except:
    #            continue 
    #        
    #        if aggregate == 'ma':
    #            output_dict['ma_avg_obs_influence_'+algorithm+'__'+str(seed_set_size)+'__'+num_samples+'__'+epsilon] = na_output_dict[algorithm][seed_set_size-1]
    #            output_dict['ma_avg_obs_regret_'+algorithm+'__'+str(seed_set_size)+'__'+num_samples+'__'+epsilon] = na_output_dict[algorithm][seed_set_size-1] - opt_influence
    #        
    #        if aggregate == 'cumsum':
    #            output_dict['avg_cumsum_obs_influence_'+algorithm+'__'+str(seed_set_size)+'__'+num_samples+'__'+epsilon] = \
    #                [ na_output_dict[algorithm][seed_set_size-1] * item for item in range(1,len(output_dict[max_key])+1)]
    #            output_dict['avg_cumsum_obs_regret_'+algorithm+'__'+str(seed_set_size)+'__'+num_samples+'__'+epsilon] = \
    #                [ (na_output_dict[algorithm][seed_set_size-1] - opt_influence) * item for item in range(1,len(output_dict[max_key])+1)]
    #        
    "Saving output as a dataframe"
    columns = list(output_dict.keys())
    
    "keeping only meanigful columns"
    rm_keywords = ['nsras','cmab','ucb','0.25']
    cols = [item for item in columns if len(set(item.split('_')) & set(rm_keywords)) != 2]
    
    output_adaptive = pd.DataFrame()
    for column in cols:
        df = pd.DataFrame(output_dict[column], columns=[column])
        output_adaptive=pd.concat([output_adaptive, df], axis=1)
        #output_adaptive[column] = output_dict[column]
        
    "Keeping only columns with non-zero values"
    #output_adaptive = output_adaptive.loc[:,(output_adaptive != 0 ).any(axis=0)]    
    
    "Saving as csv"
    colnames = [name for name in output_adaptive if name.startswith(('time',aggregate,'avg_'+aggregate))]
    output_adaptive = output_adaptive[colnames]
    output_dir = compilation_temp
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    output_dir = os.path.join(output_dir, 'results'+name_id)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    csv_path = os.path.join(output_dir, 'output_adaptive.csv')
    output_adaptive.to_csv(csv_path,index=False,header=True)
    #output_non_adaptive.to_csv("output_non_adaptive.csv",index=False,header=True)
    #output.to_csv("output_avg.csv",index=False,header=True)
    
    "Saving as pickle"
    filename = 'output_adaptive.pkl'
    fstr = os.path.join(output_dir,filename)
    with open(fstr,'wb') as f:
        pickle.dump(output_adaptive, f)
    
