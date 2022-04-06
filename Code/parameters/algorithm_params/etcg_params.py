# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 14:33:43 2022

@author: Tim Schommer
"""

seed_set_size = 4
time_horizon = 10000

def validateSolo(dat):
    data = dat["params"]
    if "seed_set_size" in data:
        val = data["seed_set_size"]
        if type(val) is not int or val < 1:
            raise AttributeError("The field 'seed_set_size' must be an"
                                " integer with value at least 1")
            
    if "time_horizon" in data:
        val = data["time_horizon"]
        if type(val) is not int or val < 1:
            raise AttributeError("The field 'time_horizon' must be an"
                                " integer with value at least 1")
            
             
    
    