# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 14:28:53 2022

@author: Tim Schommer
"""

from application.application import Application
from application.application.im.network.network import buildNetwork
from application.application.im.propogation.propogation import Propogator
import networkx as nx
import os.path

class Im(Application):
    def __init__(self, params):
        self.params = params
        self.network = buildNetwork(params)
        self.prop = Propogator(self.network, params)
        
    def getReward(self, choices, spontaneous_prob=None):
        return self.prop.propogate(choices, spontaneous_prob)
        
    def getOptionCount(self):
        return self.network.number_of_nodes()
    
    def listOptions(self):
        return list(self.network.nodes())
    
    def toDataframeEdges(self):
        return nx.to_pandas_edgelist(self.network)
    
    def writeEdgelist(self, location):
        nx.write_edgelist(self.network, location)
        
    def networkPath(self):
        networkParams = ["network_id","community_id","keptId",
             "outlierId","weighting_method","uniform_weight","tvId"]
        part = self.params.get(networkParams[0])
        for i in range(1,len(networkParams)):
            part += "_" + str(self.params.get(networkParams[i]))
        return os.path.join("app-im",part)
    
    
def createInstance(params):
    return Im(params)