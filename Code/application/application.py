# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 16:18:15 2022

@author: raqua
"""

from abc import ABC, abstractmethod

class Application(ABC):
    
    @abstractmethod
    def getReward(self, choices):
        ...