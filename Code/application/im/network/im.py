# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 14:50:23 2022

@author: raqua
"""

from application.application import Application

class Im(Application):
    def __init__(self,pset):
        self.pset = pset
        
    def getReward(self, choices):
        return 1
    
    

def createInstance(pset):
    return Im(pset)