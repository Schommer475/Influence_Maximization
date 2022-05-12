# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 16:43:51 2022

@author: Tim Schommer
"""

from abc import ABC, abstractmethod
from application.application import Application
from parameters.parameterization_classes import ParamSet

class Algorithm(ABC):
    
    @abstractmethod
    def run(self, app: Application, pset: ParamSet, timestamp:str, randId:str):
        ...
        
    @abstractmethod
    def refresh(self):
        ...
        
    def newRun(self, reInit: bool):
        if reInit:
            self.refresh()
