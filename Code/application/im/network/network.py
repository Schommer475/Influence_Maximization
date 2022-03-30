# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 10:19:00 2022

@author: Tim Schommer
"""
import networkx as nx
import pickle
import random
import pandas as pd

def buildNetwork(params):
    network = None
    if params.get("use_florentine"):
        network = nx.florentine_families_graph()
        network = network.to_directed()
    else:
        network = nx.read_edgelist(params.get("network_file"),create_using=nx.DiGraph(), nodetype = int)
        with open(params.get("community_file"), 'rb') as f:
            part = pickle.load(f)
        #This part is in all the examples but doesn't appear to do anything
        #value = [part.get(node) for node in network.nodes()]
        nodes_subset = [key for key,value in part.items() if value in params.get("kept_values")]
        for outlier in params.get("outliers"):
            nodes_subset.remove(outlier)
            
        network = nx.subgraph(network, nodes_subset).copy()
        
    network = nx.convert_node_labels_to_integers(network,first_label=0)
    method = params.get("weighting_method")
    if (method == "rn"):
        for edge in network.edges():
            network[edge[0]][edge[1]]['act_prob'] = random.random()
            
    elif (method == "un"):
        w = params.get("uniform_weight")
        for edge in network.edges():
            network[edge[0]][edge[1]]['act_prob'] = w

    elif (method == "tv"):
        TV = params.get("tv_choices")
        for edge in network.edges():
            network[edge[0]][edge[1]]['act_prob'] = random.choice(TV)
            
    elif (method == "wc"):
      
      edge_list = pd.DataFrame(list(network.edges)) 
      edge_list.columns = ['from','to']
      in_degree = pd.DataFrame(list(network.in_degree))
      in_degree.columns = ['to','in_degree']
      edge_list = edge_list.merge(in_degree)
      edge_list['act_prob'] = 1./edge_list['in_degree']
      
      for i in range(len(edge_list)):
             network[edge_list['from'][i]][edge_list['to'][i]]['act_prob'] = edge_list['act_prob'][i]
             
    return network