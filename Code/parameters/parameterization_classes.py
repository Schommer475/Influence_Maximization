# -*- coding: utf-8 -*-
"""
Created on Tue May 10 18:40:39 2022

@author: Tim Schommer
"""

from namespace import namespace
from Utilities.program_vars import globals_index, applications_index, algorithms_index, \
    joint_index
from importlib import import_module
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
        
    def toDict(self):
        return {
            "package":self.package,
            "name":self.name,
            "errmsg1":self.errmsg1,
            "errmsg2":self.errmsg2
            }
    
    def fromDict(data):
        return ModuleHandler(data["package"], data["name"], data["errmsg1"], data["errmsg2"])
    
    
class ParamWrapper:
    def __init__(self, name, unique, params, modhandler):
        self.name = name
        self.unique = unique
        self.params = params
        self.modhandler = modhandler
        self.saved = None
        
        
    def get(self):
        if self.unique:
            return BaseParamSet(self.name, copy.deepcopy(self.params), self.modhandler)
        elif self.saved is None:
            self.saved = BaseParamSet(self.name, self.params, self.modhandler)
        return self.saved
    
    def reset(self):
        self.modhandler.reset()
    
class InstanceWrapper:
    def __init__(self, unique, unique_instance, pwrapper, loader):
        self.unique = unique or unique_instance
        self.pwrapper = pwrapper
        self.loader = loader
        self.saved = None
        
        
    def get(self):
        if self.unique:
            pset = self.pwrapper.get()
            return (pset, self.loader.createInstance(pset))
        elif self.saved is None:
            pset = self.pwrapper.get()
            self.saved = self.loader.createInstance(pset)
        return (self.pwrapper.get(), self.saved)
    
    def reset(self):
        self.pwrapper.reset()
        self.loader = None
    
class ExperimentWrapper:
    def __init__(self, gwrapper, gmodule):
        self.gwrapper = gwrapper
        self.appwrapper = None
        self.algwrapper = None
        self.gmodule = gmodule
        self.appmodule = None
        self.algmodule = None
        self.globals = None
        self.application = None
        self.algorithm = None
        self.paramset = None
        
    def setApp(self, appWrap, appmod):
        self.appwrapper = appWrap
        self.appmodule = appmod
        
    def setAlg(self, algWrap, algmod):
        self.algwrapper = algWrap
        self.algmodule = algmod
        
    def validate(self):
        self.globals = self.gwrapper.get()
        appPars, self.application = self.appwrapper.get()
        algPars, self.algorithm = self.algwrapper.get()
        self.paramset = ParamSet(self.globals, appPars, algPars)
        
        g_validate = (hasattr(self.gmodule,"doFullCheck") and 
            (type(self.gmodule.doFullCheck) is bool)
            and self.gmodule.doFullCheck)
        app_validate = (hasattr(self.appmodule,"doFullCheck") and 
            (type(self.appmodule.doFullCheck) is bool)
            and self.appmodule.doFullCheck)
        alg_validate = (hasattr(self.algmodule,"doFullCheck") and 
            (type(self.algmodule.doFullCheck) is bool)
            and self.algmodule.doFullCheck)
        
        if g_validate:
            self.gmodule.validateFull(self.paramset, self.application, self.algorithm)
        if app_validate:
            self.appmodule.validateFull(self.paramset, self.application, self.algorithm)
        if alg_validate:
            self.algmodule.validateFull(self.paramset, self.application, self.algorithm)
            
    def reset(self):
        self.gmodule = None
        self.appmodule = None
        self.algmodule = None
        self.paramset.reset()
        self.gwrapper.reset()
        self.appwrapper.reset()
        self.algwrapper.reset()
            
    def get(self, doRefresh):
        self.application.newRun(doRefresh)
        self.algorithm.newRun(doRefresh)
        return (self.paramset, self.application, self.algorithm)
    
    
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
    
    def reset(self):
        self.loader.reset()
        
    def toDict(self):
        return {
            "params":self.params,
            "name":self.name,
            "loader":self.loader.toDict()
            }
    
    def fromDict(data):
        return BaseParamSet(data["name"], data["params"], 
                            ModuleHandler.fromDict(data["loader"]))
    
    
    
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
    
    def toDict(self):
        return {
            "globalParams":self.globalParams.toDict(),
            "applicationParams":self.applicationParams.toDict(),
            "algorithmParams":self.algorithmParams.toDict()
            }
    
    def fromDict(data):
        return ParamSet(BaseParamSet.fromDict(data["globalParams"]), 
                        BaseParamSet.fromDict(data["applicationParams"]), 
                        BaseParamSet.fromDict(data["algorithmParams"]))