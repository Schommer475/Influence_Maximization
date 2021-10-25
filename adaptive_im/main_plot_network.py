#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 20:22:51 2019

@author: abhishek.umrawal
"""

"Importing necessary modules"

import networkx as nx
import matplotlib.pyplot as plt
#%matplotlib


"Declaring the Florentine families network"
#network = nx.florentine_families_graph()
#network = network.to_directed()
#network = nx.convert_node_labels_to_integers(network,first_label=1)

"Reading the Facebook network from file"
network = nx.read_edgelist("facebook_network.txt",create_using=nx.DiGraph(), nodetype = int)
network = network.to_directed()

"Working with a sparse subgraph"
sub_graph_size = 100
out_degree_list = []
for node in list(network.nodes):
    out_degree_list.append(network.out_degree(node))
        
out_degree_list = [x for x in out_degree_list if x>50]    
des_sorted_nodes = [x for _,x in sorted(zip([-x for x in out_degree_list],list(network.nodes)))]
network = network.subgraph(des_sorted_nodes[0:sub_graph_size])

"Relabeling the nodes as positive integers viz. 1,2,..."
network = nx.convert_node_labels_to_integers(network,first_label=1)

"Simple graph"
pos=nx.spring_layout(network)
nx.draw(network,pos,node_color='#A0CBE2',edge_color='#BB0000',width=2,edge_cmap=plt.cm.Blues,with_labels=True)
        
"Asthetic graph"
options = {
    #'node_color': 'blue',
    'node_size': 15000,
    #'width': 4,
    'arrowstyle': '-|>',
    'arrowsize': 40,
}

pos=nx.spring_layout(network)
nx.draw(network,pos, font_size = 20, font_weight='bold',font_family='times', node_color='w',edge_color='#BB0000',width=1,with_labels=True, **options)
nx.draw_networkx_nodes(network,pos, node_color='#A0CBE2', with_labels=True, node_size=15000, node_shape='o', alpha=None,)        
nx.draw_networkx_edges(network,pos, width = 3, **options)
        
plt.savefig("facebook_network.png", dpi=500, facecolor='w', edgecolor='w',orientation='portrait', papertype=None, format=None,transparent=False, bbox_inches=None, pad_inches=0.1)