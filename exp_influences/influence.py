#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 21:39:24 2018

@author: abhishek.umrawal
"""
from independent_cascade import independent_cascade
from linear_threshold import linear_threshold
import networkx as nx
import numpy as np

def influence(network, seed_set, diffusion_model, spontaneous_prob = []):
    
    nodes = list(nx.nodes(network))
    influence = 0
            
    
    spontaneously_infected = []
        
    if len(spontaneous_prob) != 0:
            
        for m in range(len(network)):
            if np.random.rand() < spontaneous_prob[m]:
                spontaneously_infected.append(nodes[m])
                    
        
    if diffusion_model == "independent_cascade":
        layers = independent_cascade(network, list(set(spontaneously_infected + seed_set)))  
        
    elif diffusion_model == "linear_threshold":
        layers = linear_threshold(network, list(set(spontaneously_infected + seed_set)))    
        
    for k in range(len(layers)):
        influence = influence + len(layers[k])
            
    influence = influence  

    return influence