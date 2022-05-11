# -*- coding: utf-8 -*-
"""
Created on Tue May 10 19:36:31 2022

@author: Tim Schommer
"""
import json

def invert_Namespace(path, inputs):
    inputs["app_first"] = not inputs["app_first"]
    global app_first
    app_first = inputs["app_first"]
    with open(path, "w") as f:
       json.dump(inputs, f, indent=6)

def toggleTimestamp_Namespace(path, inputs):
    inputs["use_timestamp"] = not inputs["use_timestamp"]
    with open(path, "w") as f:
       json.dump(inputs, f, indent=6)

def toggleRandID_Namespace(path, inputs):
    inputs["use_randID"] = not inputs["use_randID"]
    with open(path, "w") as f:
       json.dump(inputs, f, indent=6)

def toggleTimeRandBreak_Namespace(path, inputs):
    inputs["sep_after"] = not inputs["sep_after"]
    with open(path, "w") as f:
       json.dump(inputs, f, indent=6)

def toggleBreak_Namespace(path, inputs, index):
        
    inputs["separators"][index] = not inputs["separators"][index]
    
    with open(path, "w") as f:
       json.dump(inputs, f, indent=6)

def swap_Namespace(path, inputs, index1, index2):
            
    temp_sep = inputs["separators"][index1]
    temp_head = inputs["headers"][index1]
    inputs["headers"][index1] = inputs["headers"][index2]
    inputs["separators"][index1] = inputs["separators"][index2]
    inputs["headers"][index2] = temp_head
    inputs["separators"][index2] = temp_sep
    
    with open(path, "w") as f:
       json.dump(inputs, f, indent=6)

def addParam_Namespace(path, inputs, param, useSep, index):
    if index == (len(inputs["headers"])):
        inputs["headers"].append(param)
        inputs["separators"].append(useSep)
    else:
        inputs["headers"].insert(index, param)
        inputs["separators"].insert(index, useSep)
        
    with open(path, "w") as f:
       json.dump(inputs, f, indent=6)

def removeParam_Namespace(path, inputs, index):
    del inputs["headers"][index]
    del inputs["separators"][index]
    with open(path, "w") as f:
        json.dump(inputs, f, indent=6)