# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 15:19:04 2022

@author: Tim Schommer
"""
from namespace import namespace
from Utilities.program_vars import globals_index, applications_index, algorithms_index, \
    default_unique_instance, joint_index
from importlib import import_module
import os
import json
import copy


    
class ModuleHandler:
    def __init__(self,package, name, errMessage1, errMessage2):
        self.initialized = False
        self.package = package
        self.name = name
        self.module = None
        self.errmsg1 = errMessage1
        self.errmsg2 = errMessage2
        
    def get(self, name):
        if not self.initialized:
            self.module = import_module(self.name,self.package)
            self.initialized = True
        if not hasattr(self.module, name):
            raise ValueError(self.errmsg1 + name + self.errmsg2)
        return getattr(self.module, name)
    
    def reset(self):
        self.initialized = False
        self.module = None
            


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

def validateInputD(data, upperRange, name):
    if "name" not in data:
        raise ValueError(name + " in input file must all have a non-empty string field called 'name'")
    if not type(data["name"]) is str:
        raise ValueError("The field 'name' for each item in " + name +" must be a non-empty string.")
    if len(data["name"]) == 0:
        raise ValueError("The string field 'name' for each item in " + name +" must be non-empty.")
        
    if "uses" not in data:
        raise ValueError(name + " in input file must all have a non-empty list field called 'uses'")
    if not type(data["uses"]) is list:
        raise ValueError("The field 'uses' for each item in " + name +" must be a non-empty list.")
    if len(data["uses"]) == 0:
        raise ValueError("The list field 'uses' for each item in " + name +" must be non-empty.")
        
    if "unique" not in data:
        data["unique"] = False
    if type(data["unique"]) is not bool:
        raise ValueError("The field 'unique' for each item in " + name +" must be a boolean.")
        
    if "unique_instance" not in data:
        data["unique_instance"] = default_unique_instance or data["unique"]
    if type(data["unique_instance"]) is not bool:
        raise ValueError("The field 'unique_instance' for each item in " + name +" must be a boolean.")
        
    if not "params" in data:
        data["params"] = dict()
    if not type(data["params"]) is dict:
        raise ValueError("The field 'params' for each item in " + name +" is expected to be a dictionary of parameters.")
        
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

def getAndValidateInput(fileName):
    if not (os.path.exists(fileName) and os.path.isfile(fileName)):
        raise IOError("File " + str(fileName) + " does not exist or is not a file.")
    inputs = None
    with open(fileName) as f:
        inputs = json.load(f)
        
    if not "num_experiments" in inputs:
        raise ValueError("Input file expected to have a field 'num_experiments' with a positive integer.")
    if not type(inputs["num_experiments"]) is int:
        raise ValueError("The field 'num_experiments' is expected to be a positive integer.")
    if inputs["num_experiments"] < 1:
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
            validateInputD(o, inputs["num_experiments"], i)
        validateCount(inputs["num_experiments"], inputs[i], i)
        
    return inputs

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


    
class BaseParamSet:
    def __init__(self, name, pars, loader):
        self.params = pars
        self.name = name
        self.loader = loader
        
    def get(self,name: str):
        if name in self.params:
            return self.params[name]
        else:
            return self.loader.get(name)
    
    def setAttr(self,name: str, value):
        self.params[name] = value
        
    def getName(self):
        return self.name
    
    
    
class ParamSet:
    def __init__(self, globalPars, appPars, algPars):
        self.globalParams = globalPars
        self.applicationParams = appPars
        self.algorithmParams = algPars
        self.jointParams = None
        
    def get(self,section: int,name: str):
        if section == globals_index:
            return self.globalParams.get(name)
        elif section == applications_index:
            return self.applicationParams.get(name)
        elif section == algorithms_index:
            return self.algorithmParams.get(name)
        elif section == joint_index and self.jointParams is not None:
            if name in self.jointParams:
                return self.jointParams[name]
            else:
                raise ValueError("There is no field " + str(name))
        else:
            raise ValueError("Invalid parameter section identifier: " + str(section))
            
    def reset(self):
        self.globalParams.reset()
        self.applicationParams.reset()
        self.algorithmParams.reset()
    
    def setAttr(self, section: int,name: str, value):
        if section == globals_index:
            self.globalParams.setAttr(name,value)
        elif section == applications_index:
            self.applicationParams.setAttr(name,value)
        elif section == algorithms_index:
            self.algorithmParams.setAttr(name,value)
        elif section == joint_index:
            if self.jointParams is None:
                self.jointParams = dict()
            self.joinParams[name] = value
        else:
            raise ValueError("Invalid parameter section identifier: " + str(section))
    
    def getApp(self):
        return self.applicationParams.getName()
    
    def getAlg(self):
        return self.algorithmParams.getName()
    
    def getPath(self, timestamp, randId):
        return namespace.getFilePath(self, timestamp, randId)
    
    
def firstValidation(data, loadedParams):
    loadedParams["globals"].validateSolo(data["global_vars"])
    for i in ["applications", "algorithms"]:
        for dat in data[i]:
            loadedParams[i][dat["name"]].validateSolo(dat)
            
def fillOut(data,modules, backup):
    globalValues = None
    otherValues = {"application":[],"algorithm":[]}
    indices = dict()
    
    if data["unique_globals"]:
        globalValues = [BaseParamSet("",copy.deepcopy(data["global_vars"])
                     ,backup) for _ in range(data["num_experiments"])]
        for i in range(data["num_experiments"]):
            indices[i] = {"globals":i}
    else:
        globalValues = [BaseParamSet("",data["global_vars"], backup["globals"])]
        for i in range(data["num_experiments"]):
            indices[i] = {"globals":0}
            
    for key in otherValues:
        count = 0
        for item in data[key + "s"]:
            first = True
            currentInstance = None
            currentPset = None
            for r in item["ranges"]:
                for i in range(r[0],r[1]+1):
                    if item["unique_instance"] or item["unique"] or first:
                        if item["unique"] or first:
                            currentPset = BaseParamSet(item["name"]
                                , copy.deepcopy(item["params"])
                                ,backup[key+"s"][item["name"]])
                        if item["unique"] or item["unique_instance"] or first:
                            count += 1
                            currentInstance = {"params":currentPset,"instance":modules[key][item["name"]].createInstance(currentPset)}
                            otherValues[key].append(currentInstance)
                            first = False
                    indices[i][key] = count - 1
                    
    return [(globalValues[indices[i]["globals"]]
             ,otherValues["application"][indices[i]["application"]]
             ,otherValues["algorithm"][indices[i]["algorithm"]])
            for i in range(data["num_experiments"])]

def createAndValidateParams(data, modules, backup, loadedParams):
    dat = fillOut(data, modules, backup)
    ret = []
    for g, ap, al in dat:
        p = ParamSet(g, ap["params"], al["params"])
        
        if (hasattr(loadedParams["globals"],"doFullCheck") and 
            (type(loadedParams["globals"].doFullCheck) is bool)
            and loadedParams["globals"].doFullCheck):
            loadedParams["globals"].validateFull(p,ap["instance"],al["instance"])
        
        if (hasattr(loadedParams["applications"][ap["params"].getName()],"doFullCheck") and 
            (type(loadedParams["applications"][ap["params"].getName()].doFullCheck) is bool)
            and loadedParams["applications"][ap["params"].getName()].doFullCheck):
            loadedParams["applications"][ap["params"].getName()].validateFull(p,ap["instance"],al["instance"])
            
        if (hasattr(loadedParams["algorithms"][al["params"].getName()],"doFullCheck") and 
            (type(loadedParams["algorithms"][al["params"].getName()].doFullCheck) is bool)
            and loadedParams["algorithms"][al["params"].getName()].doFullCheck):
            loadedParams["algorithms"][al["params"].getName()].validateFull(p,ap["instance"],al["instance"])
            
        p.reset()
        ret.append((p, ap["instance"], al["instance"]))
        
    return ret
        


def readInFile(fileName):
    data = getAndValidateInput(fileName)
    loadedParams, modules, backup = loadModules(listModules(data))
    firstValidation(data, loadedParams)
    ret = None
    if data["unique_globals"]:
        ret = BaseParamSet("",copy.deepcopy(data["global_vars"])
                 ,backup["globals"])
    else:
        ret = BaseParamSet("",data["global_vars"], backup["globals"])
        
    return (ret, createAndValidateParams(data, modules, backup, 
             loadedParams))

