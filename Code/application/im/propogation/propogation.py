# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 11:44:05 2022

@author: Tim Schommer
"""

import networkx as nx
import random
import copy

class Propogator:
    def __init__(self, G, params):
        self.params = params
        self.propType = params.get("propogation_type")
        self.steps = params.get("propogation_steps")
        if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
            if self.propType == "independent_cascade":
              raise Exception( \
                  "independent_cascade() is not defined for graphs with multiedges.")
            elif self.propType == "linear_threshold":
                raise Exception( \
                  "linear_threshold() is not defined for graphs with multiedges.")
                    
        if not G.is_directed():
          self.DG = G.to_directed()
        else:
          self.DG = copy.deepcopy(G)
          
        if self.propType == "independent_cascade":
            w = params.get("unform_weight")
            for e in self.DG.edges():
              if 'act_prob' not in self.DG[e[0]][e[1]]:
                self.DG[e[0]][e[1]]['act_prob'] = w
              elif self.DG[e[0]][e[1]]['act_prob'] > 1:
                raise Exception("edge activation probability:", \
                    self.DG[e[0]][e[1]]['act_prob'], "cannot be larger than 1")
                    
        else:
            t = params.get("default_threshold")
            for n in self.DG.nodes():
                if 'threshold' not in self.DG.node[n]:
                  self.DG.node[n]['threshold'] = t
                elif self.DG.node[n]['threshold'] > 1:
                  raise Exception("node threshold:", self.DG.node[n]['threshold'], \
                      "cannot be larger than 1")
            
            # init influences
            in_deg = self.DG.in_degree()
            for e in self.DG.edges():
              if 'influence' not in self.DG[e[0]][e[1]]:
                self.DG[e[0]][e[1]]['influence'] = 1.0 / in_deg[e[1]]
              elif self.DG[e[0]][e[1]]['influence'] > 1:
                raise Exception("edge influence:", self.DG[e[0]][e[1]]['influence'], \
                    "cannot be larger than 1")
                      
    def propogate(self, seeds, spontaneous_prob = None):
        if spontaneous_prob is not list:
            spontaneous_prob = []
        nodes = list(nx.nodes(self.DG))
        influence = 0
                
        spontaneously_infected = []
            
        if len(spontaneous_prob) == len(self.DG):
            for m in range(len(self.DG)):
                if random.uniform() < spontaneous_prob[m]:
                    spontaneously_infected.append(nodes[m])
                        
            
        layers, tried, successes = self.basePropogate(list(set(spontaneously_infected + seeds)))  
            
        chosen = []
        for k in range(len(layers)):
            chosen = chosen + layers[k]
            influence = influence + len(layers[k])
    
        return influence, chosen, tried, successes, layers
    
    def basePropogate(self, seeds):
        for s in seeds:
            if s not in self.DG.nodes():
              raise Exception("seed", s, "is not in graph")
              
        A = copy.deepcopy(seeds)  # prevent side effect
        if self.steps <= 0:
          # perform diffusion until no more nodes can be activated
          return self._diffuse_all(self.DG, A)
        # perform diffusion for at most "steps" rounds
        scopy = self.steps
        return self._diffuse_k_rounds(self.DG, A, scopy)
    
    def _diffuse_all(self, G, A):
        tried_edges = set()
        success_edges = set()
        layer_i_nodes = [ ]
        layer_i_nodes.append([i for i in A])  # prevent side effect
        while True:
            len_old = len(A)
            (A, activated_nodes_of_this_round, cur_tried_edges, cur_success_edges) = \
                self._diffuse_one_round(G, A, tried_edges)
            layer_i_nodes.append(activated_nodes_of_this_round)
            tried_edges = tried_edges.union(cur_tried_edges)
            success_edges = success_edges.union(cur_success_edges)
            if len(A) == len_old:
                break
        return layer_i_nodes, tried_edges, success_edges
    
    def _diffuse_k_rounds(self, G, A, steps):
        tried_edges = set()
        success_edges = set()
        layer_i_nodes = [ ]
        layer_i_nodes.append([i for i in A])
        while steps > 0 and len(A) < len(G):
            len_old = len(A)
            (A, activated_nodes_of_this_round, cur_tried_edges, cur_success_edges) = \
                self._diffuse_one_round(G, A, tried_edges)
            layer_i_nodes.append(activated_nodes_of_this_round)
            tried_edges = tried_edges.union(cur_tried_edges)
            success_edges = success_edges.union(cur_success_edges)
            if len(A) == len_old:
                break
            steps -= 1
        return layer_i_nodes, tried_edges, success_edges
    
    def _diffuse_one_round(self, G, A, tried_edges):
        cascade = self.propType == "independent_cascade"
        activated_nodes_of_this_round = set()
        cur_tried_edges = set()
        cur_success_edges = set()
        for s in A:
            for nb in G.successors(s):
                if nb in A or (cascade and ((s, nb) in tried_edges or (s, nb) in cur_tried_edges)):
                    continue
                
                if self.isActivated(G, A, s, nb):
                    activated_nodes_of_this_round.add(nb)
                    cur_success_edges.add((s,nb))
                cur_tried_edges.add((s, nb))
        activated_nodes_of_this_round = list(activated_nodes_of_this_round)
        A.extend(activated_nodes_of_this_round)
        return A, activated_nodes_of_this_round, cur_tried_edges, cur_success_edges
    
    def _isActivated(self, G, A, src, dest):
        if self.propType == "independent_cascade":
            return self._prop_success(G, src, dest)
        else:
            src = list(set(G.predecessors(dest)).intersection(set(A)))
            return self._threshold_success(self, G, src, dest)
    
    def _prop_success(self, G, src, dest):
        return random.random() <= G[src][dest]['act_prob']
    
    def _threshold_success(self, G, froms, to):
        return self._influence_sum(G, froms, to) >= G.node[to]['threshold']
    
    def _influence_sum(self, G, froms, to):
        influence_sum = 0.0
        for f in froms:
            influence_sum += G[f][to]['influence']
        return influence_sum
            
        