# -*- coding: utf-8 -*-
"""
Created on Wed May 11 19:35:19 2022

@author: Tim Schommer
"""

from application.application import Application
import random

class ToyMax(Application):
    def __init__(self, params):
        self.params = params
        self.bandits = [random.random() for _ in range(self.params.get("num_choices"))]
        
    def getReward(self, choices, spontaneous_prob=None):
        r = 0
        for i in choices:
            if self.bandits[i] >= r:
                r = self.bandits[i]
                
        return r
        
    def getOptionCount(self):
        return self.params.get("num_choices")
        
    def listOptions(self):
        return [i for i in range(self.params.get("num_choices"))]
        
    def refresh(self):
        self.bandits = [random.random() for _ in range(self.params.get("num_choices"))]
        

def createInstance(params):
    return ToyMax(params)