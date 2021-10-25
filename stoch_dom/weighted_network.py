#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 16:03:00 2019

@author: abhishek.umrawal
"""

"Importing necessary modules"
import numpy as np
import pandas as pd
import os as os; os.getcwd()

def weighted_network(network, method):
    
    if (method == "rn"):
        for edge in network.edges():
            network[edge[0]][edge[1]]['act_prob'] = np.random.rand(1)[0]

    elif (method == "tv"):
        TV = [.1,.01,.001]
        for edge in network.edges():
            network[edge[0]][edge[1]]['act_prob'] = np.random.choice(TV)
            
    elif (method == "wc"):
      
      edge_list = pd.DataFrame(list(network.edges)) 
      edge_list.columns = ['from','to']
      in_degree = pd.DataFrame(list(network.in_degree))
      in_degree.columns = ['to','in_degree']
      edge_list = edge_list.merge(in_degree)
      edge_list['act_prob'] = 1./edge_list['in_degree']
      
      for i in range(len(edge_list)):
             network[edge_list['from'][i]][edge_list['to'][i]]['act_prob'] = edge_list['act_prob'][i]/5
      
    return  network