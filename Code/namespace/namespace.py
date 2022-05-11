# -*- coding: utf-8 -*-
from Utilities.global_names import global_namespace, application_namespace,\
    algorithm_namespace, joint_namespace, temp_dir
from Utilities.program_vars import applications_index, algorithms_index, \
    basic_separator
from parameters.parameter_check import checkParamExistence as checkParams
    
import json
import os.path
from os import makedirs

app_first = None
loaded_applications = dict()
loaded_algorithms = dict()
loaded_joints = dict()

data = None
if os.path.exists(global_namespace):
    with open(global_namespace,"r") as f:
        data = json.load(f)
            
if data is None:
    data = {"app_first":True}
    
if "app_first" not in data:
    raise ValueError("The global namespace file must have a bool variable 'app_first'")
    
if not type(data["app_first"]) is bool:
    raise ValueError("The variable 'app_first' in the global namespace must be a boolean")
    
app_first = data["app_first"]
data = None
    
def getAppFirst():
    return app_first
    
def getInput(section, identifier):
    data = None
    expected_header = "-" + identifier
    path = identifier + ".json"
    if section == applications_index:
        expected_header = "app" + expected_header
        path = os.path.join(application_namespace, path)
    elif section == algorithms_index:
        expected_header = "alg" + expected_header
        path = os.path.join(algorithm_namespace, path)
    else:
        raise ValueError("Invalid section value")
        
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            
    if data is None:
        data = {
            "headers":[expected_header],
            "separators":[False]
        }
    return data
    
def getAndValidateInput(section, identifier):
    data = getInput(section, identifier)
    expected_header = "-" + identifier
    if section == applications_index:
        expected_header = "app" + expected_header
    elif section == algorithms_index:
        expected_header = "alg" + expected_header
    else:
        raise ValueError("Invalid section value")
        
    if not "headers" in data:
        raise ValueError("Files describing pathing must have a string array called 'headers'")
    if not type(data["headers"]) is list:
        raise ValueError("The variable 'headers' must be a list of strings")
    for h in data["headers"]:
        if not type(h) is str:
            raise ValueError("Every entry in the list 'headers' must be a string")
            
    if not "separators" in data:
        raise ValueError("Files describing pathing must have a bool array called 'separators'")
    if not type(data["separators"]) is list:
        raise ValueError("The variable 'separators' must be a list of bools")
    for h in data["separators"]:
        if not type(h) is bool:
            raise ValueError("Every entry in the list 'separators' must be a bool")
            
    if len(data["headers"]) == 0:
        raise ValueError("The headers variable must containat least one string entry of the format <type>-<name> "
                         "where <type> is 'app' if the file represents an application and 'alg' if the file represents "
                         "an algorithm; and <name> is the name of the particular application or algorithm.")
        
    if len(data["headers"]) != len(data["separators"]):
        raise ValueError("The lists 'headers' and 'separators' must have the same length.")
        
    if data["headers"][0] != expected_header:
        raise ValueError("The first entry in 'headers' was expected to be " 
                         + expected_header + " but instead was " + data["headers"][0])
        
    if(len(data["headers"]) > 1):
        valid, offender = checkParams(section, identifier, data["headers"][1:])
        
        if not valid:
            raise ValueError("one or more path parameter names specified for " 
                             + identifier + " did not exist. First offender was: " + offender)
        
    return data
        
def getJoint(application, algorithm):
    path = os.path.join(joint_namespace, application + "_" + algorithm + ".json")
    data = None
    
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            
    if data is None:
        data = {
            "use_timestamp":False,
            "use_randID":True,
            "sep_after":False
        }
    return data

def getAndValidateJoint(application, algorithm):
    data = getJoint(application, algorithm)
    
        
    if not "use_timestamp" in data:
        raise ValueError("Files describing pathing for application-algorithm "
                         "pairs must have a bool value called 'use_timestamp'")
    if not type(data["use_timestamp"]) is bool:
        raise ValueError("'use_timestamp' must be a bool")
        
    if not "use_randID" in data:
        raise ValueError("Files describing pathing for application-algorithm "
                         "pairs must have a bool value called 'use_randID'")
    if not type(data["use_randID"]) is bool:
        raise ValueError("'use_randID' must be a bool")
        
    if not "sep_after" in data:
        raise ValueError("Files describing pathing for application-algorithm "
                         "pairs must have a bool value called 'sep_after'")
    if not type(data["sep_after"]) is bool:
        raise ValueError("'sep_after' must be a bool")
        
    return data

def buildBaseSection(section, data, inputs):
    path = data["headers"][0]
    for i in range(1,len(data["separators"])):
        if data["separators"][i-1]:
            path += os.path.sep
        else:
            path += basic_separator
        path += str(inputs.get(section,data["headers"][i]))
        
    return (path, data["separators"][-1])

def buildJointSection(data, timestamp, randomId):
    path = ""
    if data["use_timestamp"]:
        path += timestamp
        if data["use_randID"]:
            path += basic_separator
    if data["use_randID"]:
        path += randomId
        
    return (path, data["sep_after"])

def orderInfo(appInfo, algInfo, jointInfo):
    if app_first:
        return (appInfo, algInfo, jointInfo)
    return (algInfo, appInfo, jointInfo)

def getFilePath(inputs, timestamp, randId):
    app_data = None;
    alg_data = None;
    joint_data = None;
    base_path = temp_dir
    
    #obtain the data about path construction
    name = inputs.getApp()
    app_name = name
    if name in loaded_applications:
        app_data = loaded_applications[name]
    else:
        app_data = getAndValidateInput(applications_index, name)
        loaded_applications[name] = app_data
        
    name = inputs.getAlg()
    alg_name = name
    if name in loaded_algorithms:
        alg_data = loaded_algorithms[name]
    else:
        alg_data = getAndValidateInput(algorithms_index, name)
        loaded_algorithms[name] = alg_data
        
    
    
    jointName = app_name + "_" + alg_name
    if jointName in loaded_joints:
        joint_data = loaded_joints[jointName]
    else:
        joint_data = getAndValidateJoint(app_name, alg_name)
        loaded_joints[jointName] = joint_data
        
    firstData, secondData, jointData = orderInfo((applications_index, app_data), 
                            (algorithms_index, alg_data), (joint_data, timestamp, randId))
    
    firstPart, firstBreak = buildBaseSection(*firstData, inputs)
    secondPart, secondBreak = buildBaseSection(*secondData, inputs)
    jointPart, jointBreak = buildJointSection(*jointData)
    path = os.path.join(base_path, firstPart)
    if firstBreak:
        path = os.path.join(path, secondPart)
    else:
        path += basic_separator + secondPart
        
    if jointPart != "":
        path = os.path.join(path, jointPart)
        if jointBreak:
            path += os.path.sep
        else:
            path += basic_separator
    else:
        if secondBreak:
            path += os.path.sep
        else:
            path += basic_separator
            
    index = path.rfind(os.path.sep)
    if index != -1:
        makedirs(path[:index], exist_ok=True)
    
    return path
    