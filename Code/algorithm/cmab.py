# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 14:50:04 2022

@author: raqua
"""

from algorithm.algorithm import Algorithm

class Cmab(Algorithm):
    def __init__(self,pset):
        self.pset = pset
        
    def run(self, choices):
        return 1
    
    

def createInstance(pset):
    return Cmab(pset)