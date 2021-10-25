#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 00:22:43 2020

@author: abhishek.umrawal
"""

"Importing required modules"
import numpy as np
import pandas as pd
import os
os.system("ls -l")
import networkx as nx
import community
import warnings
warnings.filterwarnings('ignore')

def subgraph(network, method, size=100):
    
    if method == "sparse":
        out_degree_list = []
        for node in list(network.nodes):
            out_degree_list.append(network.out_degree(node))
        
        out_degree_list = [x for x in out_degree_list if x>np.mean(out_degree_list)]    
        des_sorted_nodes = [x for _,x in sorted(zip([-x for x in out_degree_list],list(network.nodes)))]
        subgraph = network.subgraph(des_sorted_nodes[0:size])
    
    if method == "louvain":
        "Community detection using python-louvain (community package)"
        part = community.best_partition(nx.Graph(network))

        "Calculating summary statistics for different communities"
        avg_degrees = []
        for val in list(set(part.values())):
            nodes_subset = [key for key,value in part.items() if value == val]
            subgraph = nx.subgraph(nx.Graph(network),nodes_subset)
            avg_degrees.append(np.mean(list(dict(subgraph.degree).values())))
    
        "Selecting a specific community and creating a subgraph"
        val = np.argmin(abs(avg_degrees - np.mean(list(dict(nx.Graph(network).degree).values()))))
        nodes_subset = [key for key,value in part.items() if value == val] 
        subgraph = nx.subgraph(nx.Graph(network),nodes_subset)
        
    if method == "infomap":
        "Writing the given network as a .net file"
        nx.write_pajek(network,'infomap_input/network.net')
        
        "Running Infomap through termminal to detect the communities"
        os.system('infomap -d infomap_input/network.net infomap_output --clu')
        
        "Reading the results of Infomap"
        data=pd.read_table('infomap_output/network.clu',skiprows=range(1))
        
        "Extracting the nodes and community labels"
        nodes = []
        community_labels = []
        for row in data['# node module flow']:
            nodes.append(int(row.split(" ")[0]))
            community_labels.append(int(row.split(" ")[1]))
        nodes = [x-1 for x in nodes]
        
        
        "Creating a list of communities: a community is a list of nodes in that community"
        communities = []
        for label in list(np.unique(np.array(community_labels))):
            communities.append([nodes[i] for i,x in enumerate(community_labels) if x == label])
        
        "Reformating communities data"   
        part = {}
        i = 0
        for com in communities:
            for node in com:
                part[node] = i
            i = i+1
            
        "Calculating summary statistics for different communities"
        avg_degrees = []
        for val in list(set(part.values())):
            nodes_subset = [key for key,value in part.items() if value == val]
            subgraph = nx.subgraph(nx.Graph(network),nodes_subset)
            avg_degrees.append(np.mean(list(dict(subgraph.degree).values())))
    
        "Selecting a specific community and creating a subgraph"
        val = np.argmin(abs(avg_degrees - np.mean(list(dict(nx.Graph(network).degree).values()))))
        nodes_subset = [key for key,value in part.items() if value == val] 
        subgraph = nx.subgraph(nx.Graph(network),nodes_subset)
        
    #subgraph = subgraph.to_directed()
    #subgraph = nx.convert_node_labels_to_integers(network,first_label=1)
    return subgraph     