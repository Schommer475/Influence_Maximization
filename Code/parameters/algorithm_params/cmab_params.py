# -*- coding: utf-8 -*-
"""
Created on Wed May 11 18:22:51 2022

@author: Tim Schommer
"""
from parameters.parameterization_classes import ParamSet
from application.application import Application
from algorithm.algorithm import Algorithm
from Utilities.program_vars import joint_index, algorithms_index
import numpy as np

seed_set_size = 4
time_horizon = 10000
error_prob = 1

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
            
    if "error_prob" in data:
        val = data["error_prob"]
        if (type(val) is not int and type(val) is not float)or val < 1:
            raise AttributeError("The field 'error_prob' must be a"
                                " number with value at least 1")
            
            
def validateFull(params: ParamSet, app: Application, alg: Algorithm):
    N = app.getOptionCount()
    K = params.get(algorithms_index, "seed_set_size")
    params.setAttr(joint_index, "N", N)
    params.setAttr(joint_index, "num_groups", int(np.ceil(N/(K+1))))
    T = params.get(algorithms_index, "time_horizon")
    precision = np.power(((N*np.log(2*N*T*alg.error_prob))/T), 1/3)
    params.setAttr(joint_index, "precision", precision)