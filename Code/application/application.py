# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 16:18:15 2022

@author: Tim Schommer
"""

from abc import ABC, abstractmethod

class Application(ABC):
    
    @abstractmethod
    def getReward(self, choices, spontaneous_prob=None):
        ...
        
    @abstractmethod
    def getOptionCount(self):
        ...
        
    @abstractmethod
    def listOptions(self):
        ...