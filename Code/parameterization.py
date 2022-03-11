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
    ret["params"].append(("globals",".global_parameters","parameters"))
    
    expected = dict()
    
    for tp in ["application", "algorithm"]:
        for item in data[tp + "s"]:
            if item["name"] not in expected:
                expected[item["name"]] = {
                    "params":{"section":tp+"s",
                              "package":["parameters",tp+"_params"],
                              "module":item["name"] + "_params"
                              },
                    "usage":{"package":tp,
                             "module": item["name"]
                            }
                    }
                
    for item in expected:
        it = expected[item]["params"]
        p1 = os.path.join(it["package"])
        p2 = ".".join(it["package"])
        pth = os.path.join(p1,it["module"]+".py")
        if not os.path.exists(pth):
            raise ValueError("There is no parameter file: " + pth)
        ret["params"].append((it["section"], p2, "."+it["module"]))
        
    for package in ["application", "algorithm"]:
        for path, directories, files in os.path.walk(package):
            for file in files:
                if len(file) > 3 and file[:-3] in expected:
                    it = expected[file[:-3]]["usage"]
                    truePackage = path.replace(os.path.sep, ".")
                    name = "." + it["module"]
                    ret["builders"].append((it["package"],truePackage,name))
                    del expected[file[:-3]]
                    
    if len(expected) > 0:
        remaining = [x for x in expected]
        raise ValueError("Could not find implementation files for: " 
             + str(remaining))
        
    return ret
                    
def loadModules(data):
    pass




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
    
    def getPath(self, timestamp, randId):
        return namespace.getFilePath(self, timestamp, randId)
    

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