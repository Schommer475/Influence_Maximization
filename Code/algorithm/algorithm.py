# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 16:43:51 2022

@author: raqua
"""

from abc import ABC, abstractmethod
from application.application import Application

class Algorithm(ABC):
    
    @abstractmethod
    def run(self, app: Application):
        ...