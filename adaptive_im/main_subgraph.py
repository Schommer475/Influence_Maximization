#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 17:37:20 2019

@author: cjquinn
"""

"Importing required modules"
import numpy as np
import os
os.system("ls -l")
import networkx as nx
import community #install python-louvain packaage by doing pipe install python-louvain on terminal
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [15,15]
import warnings
warnings.filterwarnings('ignore')
from weighted_network import weighted_network
import random

"Reading the Facebook network from file"
network = nx.read_edgelist("facebook_network.txt",create_using=nx.DiGraph(), nodetype = int)
network = weighted_network(network,'wc')

"Community detection using python-louvain (community package)"
random.seed(1234)
part = community.best_partition(nx.Graph(network))

"Plotting commuities"
values = [part.get(node) for node in network.nodes()]
#nx.draw_spring(network, cmap = plt.get_cmap('jet'), node_color = values, node_size=30, with_labels=False)

"Calculating summary statistics for different communities"
network.name = "Whole network"
print("\n")
print(nx.info(nx.Graph(network)))
#betweenness = np.mean(list(nx.betweenness_centrality(nx.Graph(network)).values()))
#print("Avg betweenness: " + str(round(betweenness,5)))
print("\n")
avg_degrees = []
for val in list(set(part.values())):
    nodes_subset = [key for key,value in part.items() if value == val]
    subgraph = nx.subgraph(nx.Graph(network),nodes_subset)
    avg_degrees.append(np.mean(list(dict(subgraph.degree).values())))
    subgraph.name = "Community "+str(val)
    print(nx.info(subgraph))
    #betweenness = np.mean(list(nx.betweenness_centrality(subgraph).values()))
    #print("Avg betweenness: " + str(round(betweenness,5)))
    print("\n")

"Selecting a specific community and creating a subgraph"
val = np.argmin(abs(avg_degrees - np.mean(list(dict(nx.Graph(network).degree).values()))))
nodes_subset = [key for key,value in part.items() if value == val] 
subgraph = nx.subgraph(nx.Graph(network),nodes_subset)
subgraph.name = "Community "+str(val)
print(nx.info(subgraph))
#betweenness = np.mean(list(nx.betweenness_centrality(subgraph).values()))
#print("Avg betweenness: " + str(round(betweenness,5)))
subgraph = subgraph.to_directed()
nx.draw_spring(subgraph, cmap = plt.get_cmap('jet'), node_color = 'b', node_size=40, with_labels=False)

"Plotting the original network and selected sub-network"
for key in part.keys():
    if part[key] == 8:
        part[key] = 1
    else:
        part[key] = 0
values = [part.get(node) for node in network.nodes()]
nx.draw_spring(network, cmap = plt.get_cmap('jet'), node_color = values, node_size=30, with_labels=False)
plt.savefig("facebook_subnetwork.png", dpi=500, facecolor='w', edgecolor='w',orientation='portrait', papertype=None, format=None,transparent=False, bbox_inches=None, pad_inches=0.1)