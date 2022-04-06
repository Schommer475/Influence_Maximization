# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 15:31:35 2022

@author: Tim Schommer
"""
from Utilities.global_names import resources, facebook_network, communities
import os.path

network_file = os.path.join(resources, facebook_network)
community_file = os.path.join(resources, communities)
kept_values = [4]
outliers = [1684]
use_florentine = False
network_id = "fb"
community_id = "fb-comm"
keptId = "4"
outlierId = "1684"

valid_weighting_methods = ["rn","un","tv","wc"]
weighting_method = "un"
uniform_weight = 0.1
tv_choices = [.1,.01,.001]
tvId = ".1-.01-.001"

valid_prop_types = ["independent_cascade", "linear_threshold"]
prop_types = {"independent_cascade":"ic","linear_threshold":"lt"}
propogation_type = "independent_cascade"
propTypeId = "ic"
propogation_steps = 0

default_threshold = 0.5


def validateSolo(data):
    p = data["params"]
    if "use_florentine" in p:
        val = p["use_florentine"]
        if type(val) is not bool:
            raise AttributeError("The field 'use_florentine' must be type bool.")
        if val:
            p["network_id"] = "fl"
            p["community_id"] = "na"
        else:
            p["network_id"] = "fb"
            p["community_id"] = "fb-comm"
    if "network_file" in p:
        if type(p["network_file"]) is not str:
            raise AttributeError("The field 'network_file' must be type string.")
        if not os.path.exists(p["network_file"]):
            raise AttributeError("The 'network_file' does not exist.")
    if "community_file" in p:
        if type(p["community_file"]) is not str:
            raise AttributeError("The field 'community_file' must be type string.")
        if not os.path.exists(p["community_file"]):
            raise AttributeError("The 'community_file' does not exist.")
    if "kept_values" in p: 
        if type(p["kept_values"]) is not list:
            raise AttributeError("The field 'kept_values' must be a non-empty list.")
        val = p["kept_values"]
        if len(val) == 0:
            raise AttributeError("The field 'kept_values' must be non-empty.")
        s = str(val[0])
        for i in range(1,len(val)):
            s += "-" + str(val[i])
        p["keptId"] = s
    if "outliers" in p:
        if type(p["outliers"]) is not list:
            raise AttributeError("The field 'outliers' must be a list.")
        val = p["outliers"]
        if len(val) == 0:
            p["outlierId"] = "na"
        else:
            s = str(val[0])
            for i in range(1,len(val)):
                s += "-" + str(val[i])
            p["outlierId"] = s
    if "weighting_method" in p:
        val = p["weighting_method"]
        if val not in valid_weighting_methods:
            raise AttributeError("The field 'weighting_method' must be one of: " 
                 + str(valid_weighting_methods))
    if "uniform_weight" in p:
        val = p["uniform_weight"]
        if type(val) is not float and type(val) is not int:
            raise AttributeError("The field 'uniform_weight' must be a number " 
                 "between 0 and 1 inclusive.")
        if val < 0 or val > 1:
            raise AttributeError("The field 'uniform_weight' must be a number " 
                 "between 0 and 1 inclusive.")
    if "tv_choices" in p:
        val = p["tv_choices"]
        if type(val) is not list or len(val) == 0:
            raise AttributeError("The field 'tv_choices' must be a non-empty list of numbers between 0 and 1.")
        for v in val:
            if type(v) is not float and type(v) is not int:
                raise AttributeError("Every item in 'tv_choices must be a number between 0 and 1.")
            if v < 0 or v > 1:
                raise AttributeError("Every item in 'tv_choices must be between 0 and 1.")
    if "propogation_type" in p:
        val = p["propogation_type"]
        if type(val) is not str or len(val) == 0:
            raise AttributeError("The field 'propogation_type' must be a string with one of the "
                                 " following values: " + str(valid_prop_types))
        if val not in valid_prop_types:
            raise AttributeError("The field 'propogation_type' must be one of the "
                                 " following values: " + str(valid_prop_types))
        p["propTypeId"] = prop_types[val]
    
    if "propogation_steps" in p:
        val = p["propogation_steps"]
        if type(val) is not int or val < 0:
            raise ValueError("The field 'propogation_steps' must be a non-negative integer.")
            
    if "default_threshold" in p:
         val = p["default_threshold"]
         if type(val) is not float and type(val) is not int:
             raise AttributeError("The field 'default_threshold' must be a number " 
                  "between 0 and 1 inclusive.")
         if val < 0 or val > 1:
             raise AttributeError("The field 'default_threshold' must be a number " 
                  "between 0 and 1 inclusive.")
             
             
    
        
        