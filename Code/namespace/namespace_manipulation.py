# -*- coding: utf-8 -*-
"""
Created on Tue May 10 19:36:02 2022

@author: Tim Schommer
"""

from Utilities.global_names import global_namespace, application_namespace,\
    algorithm_namespace, joint_namespace, temp_dir, registered_namespace
from Utilities.program_vars import applications_index, algorithms_index, joint_index,\
    basic_separator
from parameters.parameter_check import checkParamExistence as checkParams
    
import json
import os.path
from namespace.namespace import getAndValidateInput, getAndValidateJoint, getJoint,\
    getInput
from namespace.namespace_internal import invert_Namespace, swap_Namespace, \
    toggleTimestamp_Namespace, toggleRandID_Namespace, toggleTimeRandBreak_Namespace, \
    toggleBreak_Namespace, addParam_Namespace, removeParam_Namespace
from namespace.namespace_external import invert_File, swap_File, \
    toggleTimestamp_File, toggleRandID_File, toggleTimeRandBreak_File, \
    toggleBreak_File, addParam_File, removeParam_File

def idIndex(data, val):
    if val == "<START>":
        return 0
    elif val == "<END>":
        return len(data)
    else:
        for i in range(1,len(data)):
            if val == data[i]:
                return i
        raise AttributeError(val + " is not a recognized parameter.")
        
        
def checkInt(val):
    if val[0] in ('-', '+'):
        return val[1:].isdigit()
    return val.isdigit()

def listAll():
    data = None
    if os.path.exists(registered_namespace):
        with open(registered_namespace, "r") as f:
            data = json.load(f)
            
    if data is None:
        data = {
            "applications":[],
            "algorithms":[]
        }
    if not "applications" in data:
        raise ValueError("The registered items file must have a list of applications.")
    if not type(data["applications"]) is list:
        raise ValueError("The variable 'applications' must be a list of strings")
    for h in data["applications"]:
        if not type(h) is str:
            raise ValueError("Every entry in the list 'applications' must be a string")
            
    if not "algorithms" in data:
        raise ValueError("The registered items file must have a list of algorithms.")
    if not type(data["algorithms"]) is list:
        raise ValueError("The variable 'algorithms' must be a list of strings")
    for h in data["algorithms"]:
        if not type(h) is str:
            raise ValueError("Every entry in the list 'algorithms' must be a string")
    return data


def register(section, identifier):
    i = None
    if section == applications_index:
        i = "applications"
    elif section == algorithms_index:
        i = "algorithms"
    else:
        raise ValueError("Invalid section value")
        
    if identifier == "-all":
        raise ValueError("Cannot register '-all'")
    data = listAll()
        
    if identifier not in data[i]:
        data[i].append(identifier)

    with open(registered_namespace, "w") as f:
        json.dump(data, f)
        
def deregister(section, identifier):
    i = None
    if section == applications_index:
        i = "applications"
    elif section == algorithms_index:
        i = "algorithms"
    else:
        raise ValueError("Invalid section value")
        
    if identifier == "-all":
        raise ValueError("Cannot register '-all'")
    data = listAll()
        
    if identifier in data[i]:
        data[i].remove(identifier)

    with open(registered_namespace, "w") as f:
        json.dump(data, f)
    
def get(section, identifier1, identifier2=None):
    data = None
    if section == joint_index:
        data = getJoint(identifier1, identifier2)
    else:
        data = getInput(section, identifier1)
    return data

def printIndividual(application, algorithm):
    if application is not None and algorithm is not None:
        print(application + "   -   " + algorithm + ":")
        try:
            data = getAndValidateJoint(application, algorithm)
            ret = ""
            if data["use_timestamp"]:
                ret += "Timestamp "
                if data["use_randID"]:
                    ret += basic_separator + " "
                    
            if data["use_randID"]:
                ret += "Random ID "
            elif not data["use_timestamp"]:
                ret += "Nothing "
                
            if data["sep_after"]:
                ret += "/"
            else:
                ret += basic_separator
                
            print(ret)
        except Exception as e:
            print("Error: " + str(e))
    else:
        section = None
        name = None
        if application is not None:
            section = applications_index
            name = application
        else:
            section = algorithms_index
            name = algorithm
            
        print(name + ":")
        try:
            data = getAndValidateInput(section, name)
            ret = "<START> "
            if data["separators"][0]:
                ret += "/ "
            else:
                ret += basic_separator + " "
                
            for i in range(1, len(data["headers"])):
                ret += data["headers"][i] + " "
                if data["separators"][i]:
                    ret += "/ "
                else:
                    ret += basic_separator + " "
                    
            ret += "<END>"
            print(ret)
        except Exception as e:
            print("Error: " + str(e))
    print()

def printList(application, algorithm):
    if ((application is not None and application == "-all")
        or (algorithm is not None and algorithm == "-all")):
        items = listAll()
        if application is None:
            for a in items["algorithms"]:
                printIndividual(None, a)
        elif algorithm is None:
            for a in items["applications"]:
                printIndividual(a, None)
        else:
            for ap in items["applications"]:
                for al in items["algorithms"]:
                    printIndividual(ap, al)
    else:
        if application is None:
            printIndividual(None, algorithm)
        elif algorithm is None:
            printIndividual(application, None)
        else:
            printIndividual(application, algorithm)
            
def getListing(application, algorithm, usage, fixedMode=False, fixedVal=True):
    applications = [application]
    algorithms = [algorithm]
    allV = None
    if application == "-all" or algorithm == "-all":
        out = "About to " + usage
        if fixedMode:
            out += " to " + str(fixedVal)
        if application == "-all" and algorithm == "-all":
            out += " for all application-algorithm pairs"
        elif application == "-all":
            out += " for all applications paired with the " + algorithm + " algorithm."
        else:
            out += " for all algorithms paired with the " + application + " application."
        out += " Do you wish to proceed? (y/n)\n"
        if input(out) == "y":
            allV = listAll()
            if application == "-all":
                applications = [
                    (a, getAndValidateInput(applications_index, a))
                    for a in allV["applications"]]
            else:
                applications = [(application,
                       getAndValidateInput(applications_index, application))]
                
            if algorithm == "-all":
                algorithms = [
                    (a, getAndValidateInput(algorithms_index, a))
                    for a in allV["algorithms"]]
            else:
                algorithms = [(algorithm,
                       getAndValidateInput(algorithms_index, algorithm))]
                
            return (True, applications, algorithms)
        else:
            return (False, None, None)
    else:
        return (True, [(application,
                       getAndValidateInput(applications_index, application))],
                    [(algorithm, 
                    getAndValidateInput(algorithms_index, algorithm))])
    
def invert(fixedMode=False, fixedVal=True):
    basePath = temp_dir
    
    output_path = global_namespace
    data = None
    
    if os.path.exists(output_path):
        with open(output_path,"r") as f:
            data = json.load(f)
            
    if data is None:
        data = {"app_first":True}
        
    if "app_first" not in data:
        raise ValueError("The global namespace file must have a bool variable 'app_first'")
        
    if fixedMode and data["app_first"] == fixedVal:
        return
    invert_File(basePath)
    invert_Namespace(output_path, data)
    


def toggleTimestamp(application, algorithm, 
    default="0000-00-00-00-00-00", fixedMode=False, fixedVal=True):
    if default is None or type(default) is not str:
        raise ValueError("default must be an string specifying a timestamp in the format yyyy-MM-dd-hh-mm-ss")
        
    doRun, applications, algorithms = getListing(application, algorithm, 
                                    "toggle timestamp usage",
                                     fixedMode=fixedMode, fixedVal=fixedVal)
    if not doRun:
        print("Canceling.")
        return
    else:
        for application, appData in applications:
            for algorithm, algData in algorithms:
                joint = getAndValidateJoint(application, algorithm)
                basepath = temp_dir
                output_path = os.path.join(joint_namespace, application + "_" + algorithm + ".json")
                if (not fixedMode) or joint["use_timestamp"] != fixedVal:
                    toggleTimestamp_File(basepath, appData, algData, joint, default)
                    toggleTimestamp_Namespace(output_path, joint)
    

def toggleRandID(application, algorithm, 
    default="00000000", fixedMode=False, fixedVal=True):
    if default is None or type(default) is not str:
        raise ValueError("default must be an string specifying an eight digit random id")
        
    doRun, applications, algorithms = getListing(application, algorithm, 
                                    "toggle random id usage", 
                                     fixedMode=fixedMode, fixedVal=fixedVal)
    if not doRun:
        print("Canceling.")
        return
    else:
        for application, appData in applications:
            for algorithm, algData in algorithms:
                joint = getAndValidateJoint(application, algorithm)
                basepath = temp_dir
                output_path = os.path.join(joint_namespace, application + "_" + algorithm + ".json")
                if (not fixedMode) or joint["use_randID"] != fixedVal:
                    toggleRandID_File(basepath, appData, algData, joint, default)
                    toggleRandID_Namespace(output_path, joint)

def toggleTimeRandBreak(application, algorithm, fixedMode=False, fixedVal=True):
    
    doRun, applications, algorithms = getListing(application, algorithm, 
                                    "toggle the usage of path separators after"
                                    " timestamps and random ids", 
                                     fixedMode=fixedMode, fixedVal=fixedVal)
    if not doRun:
        print("Canceling.")
        return
    else:
        for application, appData in applications:
            for algorithm, algData in algorithms:
                joint = getAndValidateJoint(application, algorithm)
                basepath = temp_dir
                output_path = os.path.join(joint_namespace, application + "_" + algorithm + ".json")
    
            if (not fixedMode) or joint["sep_after"] != fixedVal:
                if not (joint["use_timestamp"] or joint["use_randID"]):
                    toggleTimeRandBreak_Namespace(output_path, joint)
                else:
                    appData = getAndValidateInput(applications_index, application)
                    algData = getAndValidateInput(algorithms_index, algorithm)
                    basepath = temp_dir
                    toggleTimeRandBreak_File(basepath, appData, algData, joint)
                    toggleTimeRandBreak_Namespace(output_path, joint)

def toggleBreak(section, identifier, index, fixedMode=False, FixedVal=False):
    data = getAndValidateInput(section, identifier)
    if checkInt(index):
        index = int(index)
    else:
        index = idIndex(data, index)
    if (not fixedMode) or (not data["separators"][index] == FixedVal):
        basepath = temp_dir
        output_path = identifier + ".json"
        if section == applications_index:
            output_path = os.path.join(application_namespace, output_path)
        else:
            output_path = os.path.join(algorithm_namespace, output_path)
        toggleBreak_File(basepath, section, index, data)
        toggleBreak_Namespace(output_path, data, index)

def swap(section, identifier, index1, index2):
    data = getAndValidateInput(section, identifier)
    
    if checkInt(index1):
        index1 = int(index1)
    else:
        index1 = idIndex(data, index1)
        
    if checkInt(index2):
        index2 = int(index2)
    else:
        index2 = idIndex(data, index2)
        
    if index1 <= 0 or index1 >= len(data["headers"]):
        raise ValueError("Index 1 out of bounds")
    if index2 <= 0 or index2 >= len(data["headers"]):
        raise ValueError("Index 2 out of bounds")
        
    if index1 != index2:
        basepath = temp_dir
        output_path = identifier + ".json"
        if section == applications_index:
            output_path = os.path.join(application_namespace, output_path)
        else:
            output_path = os.path.join(algorithm_namespace, output_path)
        swap_File(basepath, section, index1, index2, data)
        swap_Namespace(output_path, data, index1, index2)

def addParam(section, identifier, param, useSep, index, default):
    data = getAndValidateInput(section, identifier)
    if checkInt(index):
        index = int(index)
    else:
        index = idIndex(data, index)
        
    if index <= 0 or index > len(data["headers"]):
        raise ValueError("Index out of bounds")
        
    if default is None or type(default) is not str:
        raise ValueError("Default must be a string value")
        
    valid, culprit = checkParams(section, identifier, [param])
    if not valid:
        raise ValueError("Module " + identifier + " does not use a parameter called '" 
                         + param + "' to add to the path")
        
    if param in data["headers"]:
        return
        
    basepath = temp_dir
    output_path = identifier + ".json"
    if section == applications_index:
        output_path = os.path.join(application_namespace, output_path)
    else:
        output_path = os.path.join(algorithm_namespace, output_path)
    addParam_File(basepath, section, index, default, useSep, data)
    addParam_Namespace(output_path, data, param, useSep, index)

def removeParam(section, identifier, index, default):
    data = getAndValidateInput(section, identifier)
    
    if checkInt(index):
        index = int(index)
    else:
        index = idIndex(data, index)
        
    if index <= 0 or index > len(data["headers"]):
        raise ValueError("Index out of bounds")
        
    if default is None or type(default) is not str:
        raise ValueError("Default must be a string value")
        
    basepath = temp_dir
    output_path = identifier + ".json"
    if section == applications_index:
        output_path = os.path.join(application_namespace, output_path)
    else:
        output_path = os.path.join(algorithm_namespace, output_path)
    removeParam_File(basepath, section, default, index, data)
    removeParam_Namespace(output_path, data, index)