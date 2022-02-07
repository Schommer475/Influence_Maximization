# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 15:19:04 2022

@author: Tim Schommer
"""
from namespace import namespace
from Utilities.program_vars import globals_index, applications_index, algorithms_index, \
    default_unique_instance
from importlib import import_module
import os
import json
import copy

loadedParams = dict()
loadedParams["globals"] = None
loadedParams["applications"] = dict()
loadedParams["algorithms"] = dict()

def lookupParams(section: int,outerName: str, innerName: str):
    if section == globals_index:
        if innerName in loadedParams["globals"].names:
            return getattr(loadedParams["globals"],innerName)
        else:
            raise ValueError("'" + str(innerName) + "' is not a known global variable.")
    elif section == applications_index:
        if outerName in loadedParams["applications"]:
            if innerName in loadedParams["applications"][outerName]:
                return getattr(loadedParams["applications"][outerName], innerName)
            else:
                raise ValueError("'" + str(innerName) + "' is not a known variable in the application " + str(outerName))
        else:
            raise ValueError("'" + str(innerName) + "' is not an application listed in the input file.")
    elif section == algorithms_index:
        if outerName in loadedParams["algorithms"]:
            if innerName in loadedParams["algorithms"][outerName]:
                return getattr(loadedParams["algorithms"][outerName], innerName)
            else:
                raise ValueError("'" + str(innerName) + "' is not a known variable in the algorithm " + str(outerName))
        else:
            raise ValueError("'" + str(innerName) + "' is not an algorithm listed in the input file.")
    else:
        raise ValueError("Invalid parameter section identifier: " + str(section))




class ParamSet:
    def __init__(self, appName, algName, globalPars, appPars, algPars):
        self.globalParams = globalPars
        self.applicationParams = appPars
        self.algorithmParams = algPars
        self.applicationName = appName
        self.algorithmName = algName
        
    def get(self,section: int,name: str):
        if section == globals_index:
            if name in self.globalParams:
                return self.globalParams[name]
            else:
                return lookupParams(section, "globals", name)
        elif section == applications_index:
            if name in self.applicationParams:
                return self.applicationParams[name]
            else:
                return lookupParams(section, self.applicationName, name)
        elif section == algorithms_index:
            if name in self.algorithmParams:
                return self.algorithmParams[name]
            else:
                return lookupParams(section, self.algorithmName, name)
        else:
            raise ValueError("Invalid parameter section identifier: " + str(section))
    
    def setAttr(self, section: int,name: str, value):
        if section == globals_index:
            self.globalParams[name] = value
        elif section == applications_index:
            self.applicationParams[name] = value
        elif section == algorithms_index:
            self.algorithmParams[name] = value
        else:
            raise ValueError("Invalid parameter section identifier: " + str(section))
    
    def getApp(self):
        return self.applicationName
    
    def getAlg(self):
        return self.algorithmName
    
    def getPath(self):
        return namespace.getFilePath(self)
    

def fill(inputs, toFill, count, varName, debugName):
    for item in inputs[varName]:
        if (("uses" not in item) or (not(type(item["uses"] is list)))
            or (len(item["uses"]) == 0)):
            raise ValueError("Each " + debugName + " variable listing in input file is expected to have a variable "
                         +"'uses' with a non-empty list")
        else:
            for use in item["uses"]:
                if (type(use) is int):
                    index = use - 1
                    if index < count:
                        if toFill[index] is not None:
                            raise ValueError("Multiple " + debugName + " uses of index " + str(index + 1))
                        else:
                            toFill[index] = item
                else:
                    _range = use.split("-")
                    if len(_range) > 2:
                        raise ValueError("Use ranges in inputs must contain at most two numbers(" + debugName + "): " + use)
                    elif len(_range) == 1:
                        index = int(use) - 1
                        if index < count:
                            if toFill[index] is not None:
                                raise ValueError("Multiple " + debugName + " uses of index " + str(index + 1))
                            else:
                                toFill[index] = item
                    else:
                        start = int(_range[0]) - 1
                        end = int(_range[1]) - 1
                        if end >= count:
                            end = count
                        if start == end:
                            index = start
                            if toFill[index] is not None:
                                raise ValueError("Multiple " + debugName + " uses of index " + str(index + 1))
                            else:
                                toFill[index] = item
                        elif start < end:
                            for index in range(start, end + 1):
                                if toFill[index] is not None:
                                    raise ValueError("Multiple " + debugName + " uses of index " + str(index + 1))
                                else:
                                    toFill[index] = item
                        
    emptyCount = 0
    empty = []
    for i in range(count):
        if toFill[i] is None:
            emptyCount += 1
            empty.append(str(i + 1))
            
    if emptyCount > 0:
        raise ValueError("Listings for " + debugName + " parameters must cover the full range from 1 to " + str(count)
                         + " Missing indices are: " + str(empty))
    
def readIn(fileName: str):
    if not (os.path.exists(fileName) and os.path.isfile(fileName)):
        raise IOError("File " + str(fileName) + " does not exist or is not a file.")
    else:
        loadedParams["globals"] = import_module(".global_parameters","parameters")
        with open(fileName) as f:
            inputs = json.load(f)
            if (("num_experiments" not in inputs) or (not(type(inputs["num_experiments"]) is int)) 
                or (inputs["num_experiments"] < 1)):
                raise ValueError("Input file is expected to have an integer variable "
                                 +"'num_experiments' with a value of at least 1")
            elif (("global_vars" not in inputs) or (not(type(inputs["global_vars"] is list)))
                or (len(inputs["global_vars"]) == 0)):
                raise ValueError("Input file is expected to have a variable "
                             +"'global_vars' with a non-empty list")
            elif (("applications" not in inputs) or (not(type(inputs["applications"] is list)))
                or (len(inputs["applications"]) == 0)):
                raise ValueError("Input file is expected to have a variable "
                             +"'applications' with a non-empty list")
            elif (("algorithms" not in inputs) or (not(type(inputs["algorithms"] is list)))
                or (len(inputs["algorithms"]) == 0)):
                raise ValueError("Input file is expected to have a variable "
                             +"'algorithms' with a non-empty list")
            else:
                count = inputs["num_experiments"]
                globs = [None for _ in range(count)]
                apps = [None for _ in range(count)]
                algs = [None for _ in range(count)]
                
                fill(inputs, globs, count, "global_vars", "global")
                fill(inputs, apps, count, "applications", "application")
                fill(inputs, algs, count, "algorithms", "algorithm")
                
                applications_list = set()
                algorithms_list = set()
                applications_files = dict()
                algorithms_files = dict()
                
                for app in apps:
                    if (("name" not in app) or (not(type(app["name"] is str)))
                        or (len(app["name"]) == 0)):
                        raise ValueError("Each application and algorithm variable listing " 
                                         + "in input file is expected to have a non-empty string variable 'name'")
                    else:
                        app["instance"] = None
                        oname = app["name"]
                        name = oname + "_params"
                        if oname not in applications_list:
                            path = os.path.join("parameters","application_params",name + ".py")
                            if not (os.path.exists(path) and os.path.isfile(path)):
                                raise ValueError("No corresponding application parameter" 
                                                 + " file could be found for " + oname)
                            else:
                                applications_list.add(oname)
                                applications_files[oname + ".py"] = oname
                                
                for alg in algs:
                    if (("name" not in alg) or (not(type(alg["name"] is str)))
                        or (len(alg["name"]) == 0)):
                        raise ValueError("Each application and algorithm variable listing " 
                                         + "in input file is expected to have a non-empty string variable 'name'")
                    else:
                        alg["instance"] = None
                        oname = alg["name"]
                        name = oname + "_params"
                        if oname not in algorithms_list:
                            path = os.path.join("parameters","algorithm_params",name + ".py")
                            if not (os.path.exists(path) and os.path.isfile(path)):
                                raise ValueError("No corresponding algorithm parameter" 
                                                 + " file could be found for " + oname)
                            else:
                                algorithms_list.add(oname)
                                algorithms_files[oname + ".py"] = oname
                            
                #import the modules for all application and algorithm parameters
                package = "parameters.application_params"
                for app in applications_list:
                    name = "." + app + "_params"
                    loadedParams["applications"][app] = import_module(name, package)
                    
                package = "parameters.algorithm_params"
                for alg in algorithms_list:
                    name = "." + alg + "_params"
                    loadedParams["algorithms"][alg] = import_module(name, package)
                    
                    
                    
                #import the modules for all applications and algorithms to create instances from
                application_modules = dict()
                
                package = "application"
                for path, directories, files in os.path.walk(package):
                    for file in files:
                        if file in applications_files:
                            truePackage = path.replace(os.path.sep, ".")
                            name = "." + applications_files[file]
                            application_modules[applications_files[file]] = import_module(name, truePackage)
                            
                
                algorithm_modules = dict()
                
                package = "algorithm"
                for path, directories, files in os.path.walk(package):
                    for file in files:
                        if file in algorithms_files:
                            truePackage = path.replace(os.path.sep, ".")
                            name = "." + algorithms_files[file]
                            algorithm_modules[algorithms_files[file]] = import_module(name, truePackage)
                
                for app in applications_list:
                    name = "." + app 
                    loadedParams["applications"][app] = import_module(name, package)
                    
                package = "algorithm"
                for alg in algorithms_list:
                    name = "." + alg
                    loadedParams["algorithms"][alg] = import_module(name, package)
                    
                    
                #Validate every set of parameters individually
                for g in inputs["global_vars"]:
                    if "params" not in g:
                        g["params"] = dict()
                    loadedParams["globals"].validateSolo(g)
                    
                for a in inputs["applications"]:
                    if "params" not in a:
                        a["params"] = dict()
                    loadedParams["applications"][a["name"]].validateSolo(a)
                    
                for a in inputs["algorithms"]:
                    if "params" not in a:
                        a["params"] = dict()
                    loadedParams["algorithms"][a["name"]].validateSolo(a)
                
                #create and validate (if needed) ParamSet objects for each experiment
                ret = []
                for i in range(count):
                    g = globs[i]
                    ap = apps[i]
                    al = algs[i]
                    
                    glo = None
                    app = None
                    alg = None
                    
                    appInstance = None
                    algInstance = None
                    
                    if(not (("unique" in g) and (type(g["unique"]) is bool))):
                        g["unique"] = False
                        
                        
                    if(not (("unique" in ap) and (type(ap["unique"]) is bool))):
                        ap["unique"] = False
                        
                    if(not (("unique_instance" in ap) and (type(ap["unique_instance"]) is bool))):
                        ap["unique_instance"] = default_unique_instance or ap["unique"]
                        
                        
                    if(not (("unique" in al) and (type(al["unique"]) is bool))):
                        g["unique"] = False
                        
                    if(not (("unique_instance" in al) and (type(al["unique_instance"]) is bool))):
                        al["unique_instance"] = default_unique_instance or al["unique"]
                    
                    
                        
                    if g["unique"]:
                        glo = copy.deepcopy(g["params"])
                    else:
                        glo = g["params"]
                        
                    
                    
                        
                    if ap["unique"]:
                        app = copy.deepcopy(ap["params"])
                    else:
                        app = ap["params"]
                        
                        
                    if al["unique"]:
                        alg = copy.deepcopy(al["params"])
                    else:
                        alg = al["params"]
                        
                    pars = ParamSet(ap["name"], al["name"], glo, app, alg)
                    
                    if (hasattr(loadedParams["global_vars"],"doFullCheck") and 
                        (type(loadedParams["global_vars"].doFullCheck) is bool)
                        and loadedParams["global_vars"].doFullCheck):
                        loadedParams["global_vars"].validateFull(pars)
                    
                    if (hasattr(loadedParams["applications"][ap["name"]],"doFullCheck") and 
                        (type(loadedParams["applications"][ap["name"]].doFullCheck) is bool)
                        and loadedParams["applications"][ap["name"]].doFullCheck):
                        loadedParams["applications"][ap["name"]].validateFull(pars)
                        
                    if (hasattr(loadedParams["algorithms"][al["name"]],"doFullCheck") and 
                        (type(loadedParams["algorithms"][al["name"]].doFullCheck) is bool)
                        and loadedParams["algorithms"][al["name"]].doFullCheck):
                        loadedParams["algorithms"][al["name"]].validateFull(pars)
                    
                    
                    if ap["unique_instance"]:
                        appInstance = application_modules[ap["name"]].createInstance(pars)
                    else:
                        if ap["instance"] is None:
                            appInstance = application_modules[ap["name"]].createInstance(pars)
                            ap["instance"] = appInstance
                        else:
                            appInstance = ap["instance"]
                            
                    
                    if al["unique_instance"]:
                        algInstance = algorithm_modules[al["name"]].createInstance(pars)
                    else:
                        if al["instance"] is None:
                            algInstance = algorithm_modules[al["name"]].createInstance(pars)
                            al["instance"] = algInstance
                        else:
                            algInstance = al["instance"]
                    
                    ret.append((pars, appInstance, algInstance))
                    
                return ret