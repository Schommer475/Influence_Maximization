# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 15:19:04 2022

@author: Tim Schommer
"""
from operator import ge
from Utilities.program_vars import default_unique_instance, default_unique_params
from importlib import import_module
import os
import json
from parameters.parameterization_classes import ModuleHandler, ParamWrapper, \
    InstanceWrapper, ExperimentWrapper

def validateSpecification(data, name, generateMode=False):
    if "name" not in data:
        raise ValueError(name + " in input file must all have a non-empty string field called 'name'")
    if not type(data["name"]) is str:
        raise ValueError("The field 'name' for each item in " + name +" must be a non-empty string.")
    if len(data["name"]) == 0:
        raise ValueError("The string field 'name' for each item in " + name +" must be non-empty.")
        
    if "unique" not in data:
        data["unique"] = default_unique_params
    if type(data["unique"]) is not bool:
        raise ValueError("The field 'unique' for each item in " + name +" must be a boolean.")
        
    if "unique_instance" not in data and not generateMode:
        data["unique_instance"] = default_unique_instance or data["unique"]
    if not generateMode and type(data["unique_instance"]) is not bool:
        raise ValueError("The field 'unique_instance' for each item in " + name +" must be a boolean.")
        
    if not "params" in data:
        data["params"] = dict()
    if not type(data["params"]) is dict:
        raise ValueError("The field 'params' for each item in " + name +" is expected to be a dictionary of parameters.")
        
    if generateMode:
        dat = data["params"]
        for key in dat:
            val = dat[key]
            if type(val) is not list:
                raise ValueError("Every term within the params field for " + name +
                                 " in an input generation file must be a list of values to use.")

def validateExperiment(experiment, maxApplication, maxAlgorithm):
    if "application" not in experiment:
        raise ValueError("Every experiment specification must have an integer field 'application'.")
    if not type(experiment["application"]) is int:
        raise ValueError("Every experiment specification must have an integer field 'application'.")
    if experiment["application"] < 0 or experiment["application"] >= maxApplication:
        raise ValueError("The value of the application field for experiment specifiers must be between 0 (inclusive) and the number of "
            + "listed application specifications (exclusive).")
    
    if "algorithm" not in experiment:
        raise ValueError("Every experiment specification must have an integer field 'algorithm'.")
    if not type(experiment["algorithm"]) is int:
        raise ValueError("Every experiment specification must have an integer field 'algorithm'.")
    if experiment["algorithm"] < 0 or experiment["algorithm"] >= maxAlgorithm:
        raise ValueError("The value of the algorithm field for experiment specifiers must be between 0 (inclusive) and the number of "
            + "listed algorithm specifications (exclusive).")

def validateInput(inputs, generateMode=False):
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

    for type in ["applications", "algorithms"]:
        for item in inputs[type]:
            validateSpecification(item, type, generateMode)

    if not generateMode:
        if not "experiments" in inputs:
            raise ValueError("Input file expected to have a field 'experiments' with a non-empty list of objects.")
        if not type(inputs["experiments"]) is list:
            raise ValueError("The field 'experiments' is expected to be a non-empty list of objects.")
        if len(inputs["experiments"]) == 0:
            raise ValueError("The list 'experiments' must be non-empty.")
        for experiment in inputs["experiments"]:
            if not type(experiment) is dict:
                raise ValueError("Every item in 'experiments' must be a JSON object (a Python dictionary).")
            validateExperiment(experiment, len(inputs["applications"], len(inputs["algorithms"])))

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
            

def createAndValidateParams(data, modules, backup, params):
    _globals = ParamWrapper("", data["unique_globals"], data["global_vars"], backup["globals"])
    experiments = [ExperimentWrapper(_globals, params["globals"]) for _ in range(len(data["experiments"]))]
    applications = [
        {
            instanceWrapper: InstanceWrapper(
                application["unique"],
                application["unique_instance"],
                ParamWrapper(
                    application["name"],
                    application["unique"],
                    application["params"],
                    backup["applications"][application["name"]]
                ),
                modules["application"][application["name"]]
            ),
            paramModule: params["applications"][application["name"]]
        }

        for application in data["applications"]
    ]

    algorithms = [
        {
            instanceWrapper: InstanceWrapper(
                algorithm["unique"],
                algorithm["unique_instance"],
                ParamWrapper(
                    algorithm["name"],
                    algorithm["unique"],
                    algorithm["params"],
                    backup["algorithms"][algorithm["name"]]
                ),
                modules["algorithm"][algorithm["name"]]
            ),
            paramModule: params["algorithms"][algorithm["name"]]
        }
        
        for algorithm in data["algorithms"]
    ]

    for index, experiment in data["experiments"]:
        appData = applications[experiment.application]
        algData = algorithms[experiment.algorithm]
        experiments[index].setApp(appData.instanceWrapper, appData.paramModule)
        experiments[index].setAlg(algData.instanceWrapper, algData.paramModule)
                        
                        
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

