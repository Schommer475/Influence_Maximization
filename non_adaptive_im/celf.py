# -*- coding: utf-8 -*-
"""
Created on Sat Jul  3 18:17:59 2021

@author: niegu
"""

import time
import heapq
import numpy as np
import networkx as nx
from tqdm import tqdm

def compute_independent_cascade(graph, seed_nodes, prob, n_iters=10000):
    total_spead = 0

    # simulate the spread process over multiple runs
    for i in tqdm(range(n_iters)):
        np.random.seed(i)
        active = seed_nodes[:]
        new_active = seed_nodes[:]
        
        # for each newly activated nodes, find its neighbors that becomes activated
        while new_active:
            activated_nodes = []
            for node in new_active:
                neighbors = list(graph.neighbors(node))
                success = np.random.uniform(0, 1, len(neighbors)) < prob
                activated_nodes += list(np.extract(success, neighbors))

            # ensure the newly activated nodes doesn't already exist
            # in the final list of activated nodes before adding them
            # to the final list
            new_active = list(set(activated_nodes) - set(active))
            active += new_active

        total_spead += len(active)

    return total_spead / n_iters

def celf(graph, k, prob=0.1, n_iters=10000):
    """
    Find k nodes with the largest spread (determined by IC) from a igraph graph
    using the Cost Effective Lazy Forward Algorithm, a.k.a Lazy Greedy Algorithm.
    """
    start_time = time.time()

    # find the first node with greedy algorithm:
    # python's heap is a min-heap, thus
    # we negate the spread to get the node
    # with the maximum spread when popping from the heap
    gains = []
    for node in graph.nodes():
        spread = compute_independent_cascade(graph, [node], prob, n_iters)
        heapq.heappush(gains, (-spread, node))

    # we pop the heap to get the node with the best spread,
    # when storing the spread to negate it again to store the actual spread
    spread, node = heapq.heappop(gains)
    solution = [node]
    spread = -spread
    spreads = [spread]

    # record the number of times the spread is computed
    lookups = [len(graph.nodes())]
    elapsed = [round(time.time() - start_time, 3)]

    for _ in tqdm(range(k - 1)):
        node_lookup = 0
        matched = False

        while not matched:
            node_lookup += 1

            # here we need to compute the marginal gain of adding the current node
            # to the solution, instead of just the gain, i.e. we need to subtract
            # the spread without adding the current node
            _, current_node = heapq.heappop(gains)
            spread_gain = compute_independent_cascade(
                graph, solution + [current_node], prob, n_iters) - spread

            # check if the previous top node stayed on the top after pushing
            # the marginal gain to the heap
            heapq.heappush(gains, (-spread_gain, current_node))
            matched = gains[0][1] == current_node

        # spread stores the cumulative spread
        spread_gain, node = heapq.heappop(gains)
        spread -= spread_gain
        solution.append(node)
        spreads.append(spread)
        lookups.append(node_lookup)

        elapse = round(time.time() - start_time, 3)
        elapsed.append(elapse)

    return solution, spreads, elapsed, lookups

"Testing"
if __name__ == '__main__':
    import pickle
    import pandas as pd
    
    """----------------------------------"""
    """READING/INTIALIZING THE NETWORK"""
    """Working with the Facebook network """
    "Reading the Facebook network from file"
    network = nx.read_edgelist("facebook_network.txt",create_using=nx.DiGraph(), nodetype = int)
    
    "Reading communities"
    filename = 'communities.pkl'
    with open(filename, 'rb') as f:
        part = pickle.load(f)
    value = [part.get(node) for node in network.nodes()]
    nodes_subset = [key for key,value in part.items() if value == 4]
       
    "Working with a subgraph after deleting an outlier node"
    nodes_subset.remove(1684)
    network = nx.subgraph(network, nodes_subset).copy() # .copy() makes a subgraph with its own copy of the edge/node attributes
    
    #network = nx.florentine_families_graph()
    
    "Converting the subgraph to a directed graph"
    network = network.to_directed()
    
    "Relabeling the nodes as positive integers viz. 1,2,..."
    network = nx.convert_node_labels_to_integers(network,first_label=0)

    #celf_solution, celf_spreads, celf_elapsed, celf_lookups = celf(network, 32)
    
#    print('solution: ', celf_solution)
#    print('spreads: ', celf_spreads)
#    print('elapsed: ', celf_elapsed)
#    print('lookups: ', celf_lookups)
    
    #celf_solution = [0, 34, 45, 41, 53, 36, 2, 17, 527, 7, 33, 4, 56, 60, 227, 6]
    ucbgr_solution = [1, 3, 35, 4, 228, 528, 46, 7]
    
    #celf1 = compute_independent_cascade(network, celf_solution, 0.1, 10000)
    ucbgr4000 = compute_independent_cascade(network, ucbgr_solution, 0.1, 10000)
    print(ucbgr4000)