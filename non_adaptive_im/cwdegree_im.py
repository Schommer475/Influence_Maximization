#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 18:29:52 2018

@author: abhishek.umrawal
"""
from independent_cascade import independent_cascade
from linear_threshold import linear_threshold
from sklearn.cluster import KMeans
import networkx as nx
import numpy as np
import pandas as pd
import random

def cwdegree_im(network, budget, diffusion_model, spontaneous_prob = [],n_sim=5000):
    
    np.random.seed(int(random.uniform(0, 1000000)))
    
    """
    Community Weighted Degree Centrality for finding the best seed set of a user-specified budget
    
    Inputs:
        - network is a networkx object
        - budget is the user-specified marketing budget which represents the no.
          of individuals to be given the freebies
        - diffusion model is either "independent_cascade" or "linear_threshold"
        - spontaneous_prob is a vector of spontaneous adoption probabiities for
          each node
          
    Outputs:
        - best_seed_set is a subset of the set of nodes with the cardinality  
          same as the budget such that it maximizes the spread of marketing
        - max_influence is the value of maximum influence
  
    """
    J = n_sim
    nodes = list(nx.nodes(network))
    max_influence = []
    best_seed_set = []
    
    if budget == 0:
        
        influence = 0
        
        for j in range(J):
            spontaneously_infected = []
            
            if len(spontaneous_prob) != 0:
                
                for m in range(len(nodes)):
                    
                    if np.random.rand() < spontaneous_prob[m]:
                        spontaneously_infected.append(nodes[m])
                                      
            if diffusion_model == "independent_cascade":
                layers = independent_cascade(network, spontaneously_infected)  
                    
            elif diffusion_model == "linear_threshold":
                layers = linear_threshold(network, spontaneously_infected)    
                    
            for k in range(len(layers)):
                influence = influence + len(layers[k])
                        
        influence = influence/J
        max_influence.append(influence)
        best_seed_set.append(None)
    
    else:
        
        
        "Community Detection - k-Means Clustering on the Weighted Adjacency Matrix"
        adjacency_matrix = nx.adjacency_matrix(network,weight ='act_prob')
        kmeans = KMeans(n_clusters=budget, random_state=0).fit(adjacency_matrix)
        labels = kmeans.predict(adjacency_matrix)

        communities = pd.DataFrame()
        communities['node'] = nodes
        communities['label'] = labels
    
        wout_degree_list = []
        for node in nodes:
            wout_degree_list.append(network.degree(node,weight='act_prob'))
        communities['wout_degree']=wout_degree_list
        
        communities['count'] = communities.groupby(['label'])['node'].transform('count')
        communities = communities.sort_values(['count','label','wout_degree'],ascending=[0,1,0])
        
        
        idx = communities.groupby(['label'])['wout_degree'].transform(max) == communities['wout_degree']
        communities[idx]['node']

        best_seed_set = list(communities[idx]['node'])
        
        seed_set = []
        
        for node in best_seed_set:
            influence = 0
            seed_set.append(node)
            
            for j in range(J):
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
                    
            influence = influence/J
            max_influence.append(influence) 
            
    print('Done!'+'\n')        
    return best_seed_set, max_influence