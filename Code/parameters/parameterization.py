# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 15:19:04 2022

@author: Tim Schommer
"""
from Utilities.program_vars import default_unique_instance, default_unique_params
from importlib import import_module
import os
import json
from parameters.parameterization_classes import ModuleHandler, ParamWrapper, \
    InstanceWrapper, ExperimentWrapper

def validateRange(item, upper, name):
    if type(item) is int:
        if item < 0:
            raise ValueError("An item in 'uses' had negative value: " 
                             + str(item) +" (" + name + ")")
        if item >= upper:
            return None
        return [item, item]
    elif type(item) is str:
        if len(item) == 0:
            raise ValueError("Range strings in 'uses' for each item in " + name +" must be non-empty.")
        _range = item.split("-")
        if len(_range) > 2:
            raise ValueError("Use ranges in inputs for each item in " + name +" must contain at most two values.")
        elif len(_range) == 1:
            item = int(_range[0])
            if item < 0:
                raise ValueError("An item range in 'uses' had negative value: " 
                                 + str(item) +" (" + name + ")")
            if item >= upper:
                return None
            return [item, item]
        else:
            start = int(_range[0])
            end = int(_range[1])
            if start < 0:
                raise ValueError("An item range in 'uses' started with a negative value: " 
                                 + str(start) +" (" + name + ")")
            if end < 0:
                raise ValueError("An item range in 'uses' ended with a negative value: " 
                                 + str(end) +" (" + name + ")")
                
            if end >= upper:
                end = upper - 1
            
            if start > end:
                return None
            
            return [start, end]
        
    else:
        raise ValueError("The type of items in 'uses' for each item in " 
             + name 
             +" is expected to be either an int or a string indicating a range.")

def validateInputD(data, upperRange, name, useRanges=True):
    if "name" not in data:
        raise ValueError(name + " in input file must all have a non-empty string field called 'name'")
    if not type(data["name"]) is str:
        raise ValueError("The field 'name' for each item in " + name +" must be a non-empty string.")
    if len(data["name"]) == 0:
        raise ValueError("The string field 'name' for each item in " + name +" must be non-empty.")
        
    if useRanges:
        if "uses" not in data:
            raise ValueError(name + " in input file must all have a non-empty list field called 'uses'")
        if not type(data["uses"]) is list:
            raise ValueError("The field 'uses' for each item in " + name +" must be a non-empty list.")
        if len(data["uses"]) == 0:
            raise ValueError("The list field 'uses' for each item in " + name +" must be non-empty.")
    else:
        if "uses" in data:
            raise ValueError("Generator files should not define the 'uses' field.")
        
    if "unique" not in data:
        data["unique"] = default_unique_params
    if type(data["unique"]) is not bool:
        raise ValueError("The field 'unique' for each item in " + name +" must be a boolean.")
        
    if "unique_instance" not in data and useRanges:
        data["unique_instance"] = default_unique_instance or data["unique"]
    if useRanges and type(data["unique_instance"]) is not bool:
        raise ValueError("The field 'unique_instance' for each item in " + name +" must be a boolean.")
        
    if not "params" in data:
        data["params"] = dict()
    if not type(data["params"]) is dict:
        raise ValueError("The field 'params' for each item in " + name +" is expected to be a dictionary of parameters.")
        
    if not useRanges:
        dat = data["params"]
        for key in dat:
            val = dat[key]
            if type(val) is not list:
                raise ValueError("Every term within the params field for " + name +
                                 " in an input generation file must be a list of values to use.")
        
    if useRanges:
        data["ranges"] = []
        for r in data["uses"]:
            ret = validateRange(r, upperRange, name)
            if ret is not None:
                data["ranges"].append(ret)
    

def validateCount(total, lst, name):
    unfilled = {x for x in range(total)}
    
    for item in lst:
        for rng in item["ranges"]:
            for i in range(rng[0],rng[1]+1):
                if i in unfilled:
                    unfilled.remove(i)
                else:
                    raise ValueError("Multiple " + name + " uses of index: " 
                         + str(i))
                    
    if len(unfilled) > 0:
        empty = []
        for i in range(total):
            if i in unfilled:
                empty.append(i)
        raise ValueError("Listings for " + name + 
             " parameters must cover the full range from 0 to " 
             + str(total - 1) + " Missing indices are: " + str(empty))
        
def validateInput(inputs, useRanges=True):
    if not "num_experiments" in inputs and useRanges:
        raise ValueError("Input file expected to have a field 'num_experiments' with a positive integer.")
    if useRanges and not type(inputs["num_experiments"]) is int:
        raise ValueError("The field 'num_experiments' is expected to be a positive integer.")
    if useRanges and inputs["num_experiments"] < 1:
        raise ValueError("'num_experiments' must be at least 1.")
        
    if not "global_vars" in inputs:
        inputs["global_vars"] = dict()
    if not type(inputs["global_vars"]) is dict:
        raise ValueError("The field 'global_vars' is expected to be a dictionary of global parameters.")
        
    if not "unique_globals" in inputs:
        inputs["unique_globals"] = False
    if not type(inputs["unique_globals"]) is bool:
        raise ValueError("The field 'unique_globals' is expected to be a boolean.")
            
    if not "applications" in inputs:
        raise ValueError("Input file expected to have a field 'applications' with a non-empty list of objects.")
    if not type(inputs["applications"]) is list:
        raise ValueError("The field 'applications' is expected to be a non-empty list of objects.")
    if len(inputs["applications"]) == 0:
        raise ValueError("The list 'applications' must be non-empty.")
    for o in inputs["applications"]:
        if not type(o) is dict:
            raise ValueError("Every item in 'applications' must be a JSON object (a Python dictionary).")
            
    if not "algorithms" in inputs:
        raise ValueError("Input file expected to have a field 'algorithms' with a non-empty list of objects.")
    if not type(inputs["algorithms"]) is list:
        raise ValueError("The field 'algorithms' is expected to be a non-empty list of objects.")
    if len(inputs["algorithms"]) == 0:
        raise ValueError("The list 'algorithms' must be non-empty.")
    for o in inputs["algorithms"]:
        if not type(o) is dict:
            raise ValueError("Every item in 'algorithms' must be a JSON object (a Python dictionary).")
            
    for i in ["applications", "algorithms"]:
        for o in inputs[i]:
            if useRanges:
                validateInputD(o, inputs["num_experiments"], i, useRanges)
            else:
                validateInputD(o, 0, i, useRanges)
        if useRanges:
            validateCount(inputs["num_experiments"], inputs[i], i)
        
    return inputs

def getAndValidateInput(fileName):
    if not (os.path.exists(fileName) and os.path.isfile(fileName)):
        raise IOError("File " + str(fileName) + " does not exist or is not a file.")
    inputs = None
    with open(fileName) as f:
        inputs = json.load(f)
        
    return validateInput(inputs)

def listModules(data):
    ret = {"params":[], "builders":[]}
    if not os.path.exists(os.path.join("parameters","global_parameters.py")):
        raise ValueError("There must be a file 'global_parameters.py' in the parameters module.")
    ret["params"].append(("globals","","parameters",".global_parameters"))
    
    expected = dict()
    
    for tp in ["application", "algorithm"]:
        for item in data[tp + "s"]:
            if item["name"] not in expected:
                expected[item["name"]] = {
                    "params":{"section":tp,
                              "package":["parameters",tp+"_params"],
                              "module":item["name"] + "_params"
                              },
                    "usage":{"package":tp,
                             "module": item["name"]
                            }
                    }
                
    for item in expected:
        it = expected[item]["params"]
        p1 = os.path.sep.join(it["package"])
        p2 = ".".join(it["package"])
        pth = os.path.join(p1,it["module"]+".py")
        if not os.path.exists(pth):
            raise ValueError("There is no parameter file: " + pth)
        ret["params"].append((it["section"], item, p2, "."+it["module"]))
        
    for package in ["application", "algorithm"]:
        for path, directories, files in os.walk(package):
            for file in files:
                if len(file) > 3 and file[:-3] in expected:
                    it = expected[file[:-3]]["usage"]
                    truePackage = path.replace(os.path.sep, ".")
                    name = "." + it["module"]
                    ret["builders"].append((it["module"],it["package"],truePackage,name))
                    del expected[file[:-3]]
                    
    if len(expected) > 0:
        remaining = [x for x in expected]
        raise ValueError("Could not find implementation files for: " 
             + str(remaining))
        
    return ret
                    
def loadModules(data):
    loadedParams = dict()
    loadedParams["globals"] = None
    loadedParams["applications"] = dict()
    loadedParams["algorithms"] = dict()
    ret = {"application":dict(),"algorithm":dict()}
    ret2 = {"globals":dict(),"applications":dict(),"algorithms":dict()}
    for section, name, package, module in data["params"]:
        if section == "globals":
            loadedParams[section] = import_module(module,package)
            ret2[section] = ModuleHandler(package, module,
                "'", "' is not a known global variable."  )
        else:
            loadedParams[section+"s"][name] = import_module(module,package)
            ret2[section+"s"][name]= ModuleHandler(package, module,
               "'", "' is not a known variable in the " + section  + " " 
               + name)
            
    for name, section, package, module in data["builders"]:
        ret[section][name] = import_module(module,package)
        
        
    return (loadedParams,ret,ret2)

    
def firstValidation(data, loadedParams):
    loadedParams["globals"].validateSolo(data["global_vars"])
    for i in ["applications", "algorithms"]:
        for dat in data[i]:
            loadedParams[i][dat["name"]].validateSolo(dat)
            

def createAndValidateParams(data,modules, backup, params):
    _globals = ParamWrapper("", data["unique_globals"], data["global_vars"], backup["globals"])
    experiments = [ExperimentWrapper(_globals, params["globals"]) for _ in range(data["num_experiments"])]
    for category in ["applications","algorithms"]:
        for item in data[category]:
            _par = ParamWrapper(item["name"], item["unique"], item["params"], 
                backup[category][item["name"]])
            instances = InstanceWrapper(item["unique"], item["unique_instance"], _par, 
                modules[category[:-1]][item["name"]])
            pmod = params[category][item["name"]]
            for r in item["ranges"]:
                for i in range(r[0], r[1]+1):
                    if category == "applications":
                        experiments[i].setApp(instances, pmod)
                    else:
                        experiments[i].setAlg(instances, pmod)
                        
                        
    gs = _globals.get()
    for experiment in experiments:
        experiment.validate()
    for experiment in experiments:
        experiment.reset()
    _globals.reset()
    return (gs, experiments)

        


def readInFile(fileName):
    data = getAndValidateInput(fileName)
    loadedParams, modules, backup = loadModules(listModules(data))
    firstValidation(data, loadedParams)
    return createAndValidateParams(data, modules, backup, loadedParams)

