# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 09:45:53 2022

@author: Tim Schommer
"""
from Utilities.program_vars import globals_index, applications_index, algorithms_index
from importlib import import_module
import os.path

def checkParamExistence(section: int,outerName: str, *innerNames:str):
    innerNames = innerNames[0]
    path = None
    package = None
    tpname = None
    if section == globals_index:
        m = import_module(".global_parameters","parameters")
        for innerName in innerNames:
            if not hasattr(m, innerName):
                return (False, innerName)
        return (True, "")
            
    elif section == applications_index:
        path = os.path.join("parameters","application_params",outerName + "_params.py")
        package = "parameters.application_params"
        tpname = " application parameter"
    elif section == algorithms_index:
        path = os.path.join("parameters","algorithm_params",outerName + "_params.py")
        package = "parameters.algorithm_params"
        tpname = " algorithm parameter"
    else:
        raise ValueError("Invalid section value")
        
    if not (os.path.exists(path) and os.path.isfile(path)):
        raise ValueError("No corresponding" + tpname   
                         + " file could be found for " + outerName)
    else:
        name = "." + outerName + "_params"
        m = import_module(name, package)
        for innerName in innerNames:
            if not hasattr(m, innerName):
                return (False, innerName)
        return (True, "")