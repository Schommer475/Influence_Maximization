# -*- coding: utf-8 -*-
"""
Created on Mon May 10 00:17:23 2021

@author: niegu
"""

import random
import networkx as nx
import copy
import numpy as np
import math
import operator
from scipy.special import comb
import pickle
from tqdm import tqdm
import os
from Utilities.global_names import resources, facebook_network, communities

# Set l to reach confidence level 1-1/n
l = 1

epsilon = 0.4
k = 3

epsilon_prime = 5*((l*epsilon**2)/(k+l))**(1/3)

def GenerateRRSet(G):
    '''
    G[i][j]['prob']
    '''
    g_copy = copy.deepcopy(G)
    v = random.sample(G.nodes(), 1)[0]
    
    edges_to_remove = []
    
    for i,j in G.edges():
        if random.random() > G[i][j]['prob']:
            edges_to_remove.append((i,j))
            
    for e in edges_to_remove:
        g_copy.remove_edge(e[0], e[1])
        
    RRR = list(nx.descendants(g_copy, v))+[v]
    
    return(G.subgraph(RRR))

def KptEstimation(G, k):
    n = len(G.nodes())
    m = len(G.edges())
    num_iter = math.floor(np.log2(n))-1
    c = [0] * num_iter
    for i in range(num_iter):
        c[i] = (6*l*np.log(n)+6*np.log(np.log2(n)))*2**i
        # sum
        s = 0
        RR = []
        for j in range(math.floor(c[i])):
            R = GenerateRRSet(G)
            RR.append(R)
            # calculate w(R)
            w = 0
            for node in R.nodes():
                w += G.in_degree(node)
            kai = 1-(1-w/m)**k
            s += kai
        if s/c[i] > 1/(2**i):
            return((n*s/(2*c[i]), RR))
    return((1,RR))
    
def most_cover(G, R_prime):
    counts = [0]*len(G.nodes())
    newRR = copy.deepcopy(R_prime)
    for node in G.nodes():
        for rr in R_prime:
            if node in rr.nodes():
                counts[node] += 1
                
    v = np.argmax(counts)
    to_remove = []
    
    for r in newRR:
        if v in r.nodes():
            to_remove.append(r)
            
    for r in to_remove:
        newRR.remove(r)
        
    return((v, newRR))
    
def RefineKPT(G, k, kpt, epsilon_prime, R_prime):
    n = len(G.nodes())
    sk = []
    newRR = R_prime
    for j in range(k):
        vj, newRR = most_cover(G, newRR)
        sk.append(vj)
        
    lambda1 = (2+epsilon_prime)*l*n*np.log(n)*epsilon_prime**(-2)
    theta1 = lambda1/kpt
    
    R_pp = []
    for i in range(math.floor(theta1)):
        R_pp.append(GenerateRRSet(G))
        
    num_cover = 0
    for r in R_pp:
        for v in sk:
            if v in r.nodes():
                num_cover += 1
                break
    
    f = num_cover/len(R_pp)
    kpt_p = f*n/(1+epsilon_prime)
    return(max([kpt_p, kpt]))
    
def NodeSelection(G, k):
    n = len(G.nodes())
    const_lambda = (8+2*epsilon)*n*(l*np.log(n)+np.log(comb(n, k))+np.log(2))*epsilon**(-2)
    
    kpt, R_prime = KptEstimation(G, k)
    kpt_p = RefineKPT(G, k, kpt, epsilon_prime, R_prime)
    
    theta = const_lambda/kpt_p
    
    R = []
    for _ in range(math.floor(theta)):
        R.append(GenerateRRSet(G))
    
    Sk_p = []
    for i in range(k):
        vj, R = most_cover(G, R)
        Sk_p.append(vj)
        
    return(Sk_p)
    
if __name__ == '__main__':
    facebook_path = os.path.join(resources, facebook_network)
    network = nx.read_edgelist(facebook_path,create_using=nx.DiGraph(), nodetype = int)
    
    "Reading communities"
    communities_path = os.path.join(resources, communities)
    with open(communities_path, 'rb') as f:
        part = pickle.load(f)
        
    value = [part.get(node) for node in network.nodes()]
    nodes_subset = [key for key,value in part.items() if value == 4]
       
    "Working with a subgraph after deleting an outlier node"
    nodes_subset.remove(1684)
    network = nx.subgraph(network, nodes_subset).copy() # .copy() makes a subgraph with its own copy of the edge/node attributes
    
    """Working with the Florentine families network """
    "Declaring the Florentine families network"
    #network = nx.florentine_families_graph()
    #network = nx.karate_club_graph()
    """----------------------------------"""
    
    "Converting the subgraph to a directed graph"
    network = network.to_directed()
    
    "Relabeling the nodes as positive integers viz. 1,2,..."
    network = nx.convert_node_labels_to_integers(network,first_label=0)
    
    for i,j in network.edges():
        network[i][j]['prob'] = 0.1
    
#    print(GenerateRRSet(G).nodes())
#    print(G.edges())
    timp = NodeSelection(network, 5)
    
    
    
        
    
