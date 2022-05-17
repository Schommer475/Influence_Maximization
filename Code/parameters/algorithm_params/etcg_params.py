# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 14:33:43 2022

@author: Tim Schommer
"""
from parameters.parameterization_classes import ParamSet
from application.application import Application
from algorithm.algorithm import Algorithm
from Utilities.program_vars import joint_index

seed_set_size = 4
time_horizon = 10000
doFullCheck = True

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
            
def validateFull(params: ParamSet, app: Application, alg: Algorithm):
    N = app.getOptionCount()
    params.setAttr(joint_index, "N", N)
            
             
    
    