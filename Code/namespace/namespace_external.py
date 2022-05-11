# -*- coding: utf-8 -*-
"""
Created on Tue May 10 19:36:50 2022

@author: Tim Schommer
"""

from Utilities.program_vars import applications_index, algorithms_index, \
    basic_separator
    
from namespace.namespace import getAndValidateInput, getAndValidateJoint,\
    orderInfo, app_first
import os.path
from pathlib import Path
import shutil
import re

class PathingObject:
    def __init__(self, path):
        self.listing = [p.split(basic_separator) for p in path.parts]
        self.alg_index1 = -1
        self.alg_index2 = -1
        self.app_index1 = -1
        self.app_index2 = -1
        self.base_index1 = len(self.listing) - 1
        self.base_index2 = len(self.listing[self.base_index1]) -1
        for i in range(len(self.listing)):
            for j in range(len(self.listing[i])):
                if self.listing[i][j].startswith("alg-"):
                    self.alg_index1 = i
                    self.alg_index2 = j
                elif self.listing[i][j].startswith("app-"):
                    self.app_index1 = i
                    self.app_index2 = j
                    
    def appIndices(self):
        return (self.app_index1, self.app_index2)
    
    def algIndices(self):
        return (self.alg_index1, self.alg_index2)
    
    def baseIndices(self):
        return (self.base_index1, self.base_index2)
    
    def getPath(self):
        parts = [basic_separator.join(part) for part in self.listing]
        path = Path(".").joinpath(*parts)
        return path
    
    def getRoot(self):
        parts = [basic_separator.join(part) for part in self.listing]
        parts = parts[:-1]
        path = Path(".").joinpath(*parts)
        return path
    
    def getIndex(self, index1, index2, offset):
        length = len(self.listing)
        if index1 >= length or index1 < -1*length:
            raise ValueError("index1 out of bounds")
        if index2 >= len(self.listing[index1]) or index2 < -1*len(self.listing[index1]):
            raise ValueError("index2 out of bounds")
            
        if index1 < 0:
            index1 = length + index1
        if index2 < 0:
            index2 = len(self.listing[index1]) + index2
            
        if offset >= 0:
            while index1 < length:
                if offset <= (len(self.listing[index1]) -1 - index2):
                    return (index1, index2 +  offset)
                else:
                    offset -= (len(self.listing[index1]) - index2)
                    index1 += 1
                    index2 = 0
        else:
            while index1 >= 0:
                if offset >= (-1* index2):
                    return (index1, index2 +  offset)
                else:
                    offset += index2 + 1
                    index1 -= 1
                    index2 = len(self.listing[index1]) - 1
            
        raise ValueError("Offset too large or too small")
        
    def get(self, index1, index2):
        if index1 >= len(self.listing) or index1 < 0:
            raise ValueError("index1 out of bounds")
        if index2 >= len(self.listing[index1]) or index2 < 0:
            raise ValueError("index2 out of bounds")
            
        return self.listing[index1][index2]
    
    def set(self, index1, index2, val):
        if index1 >= len(self.listing) or index1 < 0:
            raise ValueError("index1 out of bounds")
        if index2 >= len(self.listing[index1]) or index2 < 0:
            raise ValueError("index2 out of bounds")
            
        self.listing[index1][index2] = val
        
    def findDeletion(self, other):
        if len(self.listing) <= len(other.listing):
            for i, val in enumerate(self.listing):
                val2 = other.listing[i]
                if len(val) != len(val2):
                    return self.listing[:i+1]
                for v1, v2 in zip(val, val2):
                    if v1 != v2:
                        return self.listing[:i+1]
            return []
        else:
            for i, val in enumerate(other.listing):
                val2 = self.listing[i]
                if len(val) != len(val2):
                    return self.listing[:i+1]
                for v1, v2 in zip(val, val2):
                    if v1 != v2:
                        return self.listing[:i+1]
            return []
                    
        return None
        
    def join(self, index:int):
        if index >= len(self.listing) - 1 or index < 0:
            raise ValueError("Invalid index")
        if index < self.alg_index1:
            self.alg_index1 -= 1
            if index == self.alg_index1:
                self.alg_index2 += len(self.listing[index])
                
        if index < self.app_index1:
            self.app_index1 -= 1
            if index == self.app_index1:
                self.app_index2 += len(self.listing[index])
                
        if index < self.base_index1:
            self.base_index1 -= 1
            if index == self.base_index1:
                self.base_index2 += len(self.listing[index])
                
        self.listing[index] = self.listing[index] + self.listing[index+1]
        del self.listing[index+1]
    
    def split(self,index1:int, index2:int):
        if index1 >= len(self.listing) or index1 < 0:
            raise ValueError("Invalid index1")
        if index2 >= len(self.listing[index1]) - 1 or index2 < 0:
            raise ValueError("Invalid index2")
            
        if index1 == self.alg_index1 and index2 < self.alg_index2:
            self.alg_index1 += 1
            self.alg_index2 -= (index2 + 1)
        elif index1 < self.alg_index1:
            self.alg_index1 +=1
            
        if index1 == self.app_index1 and index2 < self.app_index2:
           self.app_index1 += 1
           self.app_index2 -= (index2 + 1)
        elif index1 < self.app_index1:
           self.app_index1 +=1
           
        if index1 == self.base_index1 and index2 < self.base_index2:
           self.base_index1 += 1
           self.base_index2 -= (index2 + 1)
        elif index1 < self.base_index1:
            self.base_index1 +=1
           
        part1 = self.listing[index1][:index2+1]
        part2 = self.listing[index1][index2+1:]
        self.listing[index1] = part2
        self.listing.insert(index1,part1)
    
    def insert(self, index1:int, index2:int, val:str):
        if index1 >= len(self.listing) or index1 < 0:
            raise ValueError("Invalid index1")
        if index2 > len(self.listing[index1]) or index2 < 0:
            raise ValueError("Invalid index2")
            
        if index1 == self.alg_index1 and index2 <= self.alg_index2:
            self.alg_index2 += 1
            
        if index1 == self.app_index1 and index2 <= self.app_index2:
            self.app_index2 += 1
            
        if index1 == self.base_index1 and index2 <= self.base_index2:
            self.base_index2 += 1
            
        if index2 == len(self.listing[index1]):
            self.listing[index1].append(val)
        else:
            self.listing[index1].insert(index2,val)
            
        
    
    def remove(self, index1:int, index2:int):
        if index1 >= len(self.listing) or index1 < 0:
            raise ValueError("Invalid index1")
        if index2 >= len(self.listing[index1]) or index2 < 0:
            raise ValueError("Invalid index2")
            
        if index1 == self.alg_index1 and index2 < self.alg_index2:
            self.alg_index2 -= 1
        elif len(self.listing[index1]) == 1 and index1 < self.alg_index1:
            self.alg_index1 -= 1
            
        if index1 == self.app_index1 and index2 < self.app_index2:
            self.app_index2 -= 1
        elif len(self.listing[index1]) == 1 and index1 < self.app_index1:
            self.app_index1 -= 1
        
        if index1 == self.base_index1 and index2 < self.base_index2:
            self.base_index2 -= 1
        elif len(self.listing[index1]) == 1 and index1 < self.base_index1:
            self.base_index1 -= 1
            
        if len(self.listing[index1]) == 1:
            del self.listing[index1]
        else:
            del self.listing[index1][index2]
            
    def invert(self, endIndex1, endIndex2, finalSlash):
        if endIndex1 >= len(self.listing) or endIndex1 < 0:
            raise ValueError("Invalid endIndex1")
        if endIndex2 >= len(self.listing[endIndex1]) or endIndex2 < 0:
            raise ValueError("Invalid endIndex2")
            
        usesTsRand = not (endIndex1 == self.base_index1 and endIndex2 == self.base_index2)
        endSlash = ((not usesTsRand) and endIndex2 == 0) or (usesTsRand and finalSlash)
        algFirst = False
        if ((self.alg_index1 < self.app_index1) 
            or (self.alg_index1 == self.app_index1 
            and self.alg_index2 < self.app_index2)):
            algFirst = True
            
        midSlash = False
        startIndex = 0;
        if algFirst:
            midSlash = self.app_index2 == 0
            startIndex = self.alg_index1
        else:
            midSlash = self.alg_index2 == 0
            startIndex = self.app_index1
            
        if (not usesTsRand) and (not endIndex2 == 0):
            i, j = self.getIndex(endIndex1, endIndex2, -1)
            self.split(i, j)
            endIndex1 = self.base_index1
            endIndex2 = self.base_index2
            
        if not midSlash:
            if algFirst:
                i, j = self.getIndex(self.app_index1, self.app_index2, -1)
                self.split(i, j)
                endIndex1 += 1
            else:
                i, j = self.getIndex(self.alg_index1, self.alg_index2, -1)
                self.split(i, j)
                endIndex1 += 1
                
        part0 = None
        part1 = None
        part2 = None
        part3 = self.listing[endIndex1:]
        if algFirst:
            part1 = self.listing[startIndex: self.app_index1]
            part2 = self.listing[self.app_index1: endIndex1]
        else:
            part1 = self.listing[startIndex: self.alg_index1]
            part2 = self.listing[self.alg_index1: endIndex1]
            
        if startIndex == 0:
            self.listing = part2 + part1 + part3
        else:
            part0 = self.listing[:startIndex]
            self.listing = part0 + part2 + part1 + part3
            
        if algFirst:
            self.app_index1 = startIndex
            self.alg_index1 = startIndex + len(part2)
        else:
            self.alg_index1 = startIndex
            self.app_index1 = startIndex + len(part2)
            
        if not (midSlash or usesTsRand):
            self.join(endIndex1 - 1)
            
        if not endSlash:
            if algFirst:
                self.join(self.alg_index1 - 1)
            else:
                self.join(self.app_index1 - 1)

def singletonPattern(data, defaultIndex = None, defaultValue = None, earlyTermination=False, filePattern=True):
    use_default = defaultIndex is not None and defaultValue is not None
    pattern = r""
    if filePattern:
        pattern += data["headers"][0]
        for i in range(1, len(data["separators"])):
            if data["separators"][i-1]:
                pattern += os.path.sep
            else:
                pattern += basic_separator
            if use_default and i == defaultIndex:
                if earlyTermination:
                    pattern += "*"
                    return pattern
                pattern += defaultValue
            else:
                pattern += "*"
    else:
        pattern += data["headers"][0]
        for i in range(1, len(data["separators"])):
            if data["separators"][i-1]:
                pattern += "\\" + os.path.sep
            else:
                pattern += basic_separator
            if use_default and i == defaultIndex:
                if earlyTermination:
                    pattern += '[^' + basic_separator + '\\' + os.path.sep + ']*'
                    return pattern
                pattern += defaultValue
            else:
                pattern += '[^' + basic_separator + '\\' + os.path.sep + "]*"
    return pattern

def getPatterns(firstData, secondData, defaultIndex = None, defaultValue = None, filePattern=True):
    patterns = []
    pattern = ""
    #Both are None only if inversion is happening, in which case you want all paths
    if firstData is None and secondData is None:
        if filePattern:
            pattern = "**" + os.path.sep + "*"
            patterns.append(pattern)
            return patterns
        else:
            pattern = ".*"
            patterns.append(pattern)
            return patterns
    #If the first data is None, you need to do recursive search for the pattern of the second part
    elif firstData is None:
        if filePattern:
            pattern = "**" + os.path.sep + "*"
            pattern += singletonPattern(secondData, defaultIndex, defaultValue)
            if secondData["separators"][-1]:
                pattern += os.path.sep + "**" + os.path.sep + "*"
                patterns.append(pattern)
            else:
                patterns.append(pattern + basic_separator + "*")
                patterns.append(pattern + os.path.sep + "**" + os.path.sep + "*")
            return patterns
        else:
            pattern = ".*"
            pattern += singletonPattern(secondData, defaultIndex, defaultValue,filePattern=filePattern)
            pattern +=  ".*"
            patterns.append(pattern)
            return patterns
    #If the second data is None, you can directly search for the pattern of the 
    #first part, but must recursively search for things afterwards
    elif secondData is None:
        if filePattern:
            pattern += singletonPattern(firstData, defaultIndex, defaultValue)
            if firstData["separators"][-1]:
                pattern += os.path.sep + "**" + os.path.sep + "*"
                patterns.append(pattern)
            else:
                patterns.append(pattern + basic_separator + "*")
                patterns.append(pattern + basic_separator + "*" + os.path.sep + "**" + os.path.sep + "*")
            return patterns
        else:
            pattern += ".*" + singletonPattern(firstData, defaultIndex, defaultValue, filePattern=filePattern)
            if firstData["separators"][-1]:
                pattern += "\\" +os.path.sep + ".*"
                patterns.append(pattern)
            else:
                patterns.append(pattern + basic_separator + ".*")
            return patterns
    #If neither is None, you can specify the full pattern
    else:
        use_default = defaultIndex is not None and defaultValue is not None
        jointInfo = None
        if firstData["headers"][0].startswith("app-"):
            jointInfo = getAndValidateJoint(firstData["headers"][0][4:],
                        secondData["headers"][0][4:])
        else:
            jointInfo = getAndValidateJoint(secondData["headers"][0][4:],
                        firstData["headers"][0][4:])
            
        if filePattern:
            pattern += singletonPattern(firstData,filePattern=filePattern)
        else:
            pattern += ".*" + singletonPattern(firstData,filePattern=filePattern)
        if firstData["separators"][-1]:
            if filePattern:
                pattern += os.path.sep
            else:
                pattern += "\\" + os.path.sep
        else:
            pattern += basic_separator
            
        pattern += singletonPattern(secondData,filePattern=filePattern)
        
        if filePattern:
            if (jointInfo["use_timestamp"] or jointInfo["use_randID"]):
                pattern += os.path.sep
                if jointInfo["use_timestamp"]:
                    if use_default and defaultIndex == 0:
                        pattern += defaultValue
                    else:
                        pattern += "*"
                    if jointInfo["use_randID"]:
                        if use_default and defaultIndex == 1:
                            pattern += basic_separator + defaultValue
                        else:
                            pattern += basic_separator + "*"
                else:
                    if use_default and defaultIndex == 1:
                        pattern += defaultValue
                    else:
                        pattern += "*"
                if jointInfo["sep_after"]:
                    pattern += os.path.sep
                else:
                    pattern += basic_separator
                        
            elif secondData["separators"][-1]:
                pattern += os.path.sep
            else:
                pattern += basic_separator
                
            pattern += "*"
        else:
            if (jointInfo["use_timestamp"] or jointInfo["use_randID"]):
                pattern += "\\" + os.path.sep
                if jointInfo["use_timestamp"]:
                    if use_default and defaultIndex == 0:
                        pattern += defaultValue
                    else:
                        pattern += "[^" + basic_separator + "\\"+os.path.sep+"]*"
                    if jointInfo["use_randID"]:
                        if use_default and defaultIndex == 1:
                            pattern += basic_separator + defaultValue
                        else:
                            pattern += basic_separator + "[^" + basic_separator + "\\"+os.path.sep+"]*"
                else:
                    if use_default and defaultIndex == 1:
                        pattern += defaultValue
                    else:
                        pattern += "[^" + basic_separator + "\\"+os.path.sep+"]*"
                if jointInfo["sep_after"]:
                    pattern += "\\" + os.path.sep
                else:
                    pattern += basic_separator
                        
            elif secondData["separators"][-1]:
                pattern += "\\" + os.path.sep
            else:
                pattern += basic_separator
                
            pattern += "[^" + basic_separator + "\\"+os.path.sep+"]*"
        patterns.append(pattern)
        return patterns
    
    
def nonDefaultDeletions(path, firstData, secondData, defaultIndex, defaultValue):
    use_default = defaultIndex is not None and defaultValue is not None
    index = defaultIndex
    reset = False
    ret = []
    if not use_default:
        return []
    pattern = ""
    #Both are None only if inversion is happening, in which case no default is present
    if firstData is None and secondData is None:
        return []
    #If the first data is None, you need to do recursive search for the pattern of the second part
    elif firstData is None:
        pattern = "**" + os.path.sep + "*"
        pattern += singletonPattern(secondData, defaultIndex, defaultValue, True)
        for i in range(defaultIndex):
            if secondData["separators"][i]:
                index = defaultIndex - (i + 1)
                reset = True
    #If the second data is None, you can directly search for the pattern of the 
    #first part up to the default
    elif secondData is None:
        pattern += singletonPattern(firstData, defaultIndex, defaultValue, True)
        for i in range(defaultIndex):
            if firstData["separators"][i]:
                index = defaultIndex - (i + 1)
                reset = True
    #If neither is None, you can specify the full pattern
    else:
        index = defaultIndex
        jointInfo = None
        if firstData["headers"][0].startswith("app-"):
            jointInfo = getAndValidateJoint(firstData["headers"][0][4:],
                        secondData["headers"][0][4:])
        else:
            jointInfo = getAndValidateJoint(secondData["headers"][0][4:],
                        firstData["headers"][0][4:])
            
        pattern += singletonPattern(firstData)
        if firstData["separators"][-1]:
            pattern += os.path.sep
        else:
            pattern += basic_separator
            
        pattern += singletonPattern(secondData)
        
        if (jointInfo["use_timestamp"] or jointInfo["use_randID"]):
            pattern += os.path.sep
            if jointInfo["use_timestamp"]:
                pattern += "*"
                if jointInfo["use_randID"]:
                    pattern += basic_separator + "*"
            else:
                index = 0
                pattern += "*"
                    
    candidates = path.glob(pattern)
    for c in candidates:
        pt = c.parts[-1]
        subs = pt.split(basic_separator)
        start = 0
        if firstData is None and not reset:
            for i in range(len(subs)):
                if subs[i] == secondData["headers"][0]:
                    start = i
                    break
        if subs[start + index] != defaultValue:
            ret.append(c)
            
    return ret
    
    
def recursiveList(currentPath, currentDict):
    if len(currentDict) == 0:
        return [currentPath]
    else:
        ret = []
        for item in currentDict:
            cur = os.path.join(currentPath, item)
            ret += recursiveList(cur, currentDict[item])
            
        return ret

def toDelete(deletionObjects):
    toDel = dict()
    for obj in deletionObjects:
        current = toDel
        for part in obj:
            pstring = basic_separator.join(part)
            if not pstring in current:
                current[pstring] = dict()
            current = current[pstring]
            
    
    return recursiveList("",toDel)

def build(initial, insert):
    current = initial
    for part in insert:
        pstring = basic_separator.join(part)
        if not pstring in current:
            current[pstring] = dict()
        current = current[pstring]
        
def compare(old, new, current):
    if len(old) == 0 and len(new) == 0:
        current["___keepme___"]=dict()
    else:
        for key in old:
            current[key] = dict()
            if key in new:
                compare(old[key], new[key], current[key])
                
def toDelete2(old, new):
    current = dict()
    compare(old, new, current)
    return recursiveList("",current)

def getPaths(base, appData=None, algData=None, 
             defaultIndex=None, defaultValue=None):
    
    firstData, secondData, _ = orderInfo(appData, algData, None)
    patterns = getPatterns(firstData, secondData, defaultIndex, defaultValue)
    cpattern = getPatterns(firstData, secondData, defaultIndex, defaultValue, False)[0]
    matcher = re.compile(cpattern)
    
                    
    foundPaths = set()
    paths = []
    for pattern in patterns:
        p = base.glob(pattern)
        for x in p: 
            if (x.is_file() and (x.stem != ".DS_Store") and (x.stem != ".gitkeep")):
                if matcher.fullmatch(str(x)) is not None:
                    if str(x) not in foundPaths:
                        foundPaths.add(str(x))
                        paths.append(x)
             
    return paths
                        
        

def getCheckJoints(section, on_boundary):
    check_joints = True
    if section == applications_index:
        check_joints = not app_first
        check_joints = check_joints and on_boundary
    elif section == algorithms_index:
        check_joints = app_first
        check_joints = check_joints and on_boundary
    else:
        raise ValueError("Invalid section number")
        
    return check_joints

def checkJoint(pathing):
    p = pathing 
    application = p.get(*p.appIndices()).split("-")[1]
    algorithm = p.get(*p.algIndices()).split("-")[1]
    joint_data = getAndValidateJoint(application, algorithm)
    
    if joint_data["use_timestamp"] or joint_data["use_randID"]:
        return True
    
    return False
    

def extractInversionData(pathing):
    p = pathing 
    application = p.get(*p.appIndices()).split("-")[1]
    algorithm = p.get(*p.algIndices()).split("-")[1]
    
    endIndex1, endIndex2 = p.baseIndices()
    
    joint_data = getAndValidateJoint(application, algorithm)
    
    if joint_data["use_timestamp"] and joint_data["use_randID"]:
        endIndex1, endIndex2 = p.getIndex(*p.baseIndices(), -2)
    elif joint_data["use_timestamp"] or joint_data["use_randID"]:
        endIndex1, endIndex2 = p.getIndex(*p.baseIndices(), -1)
            
    endSlash = False
    algData = getAndValidateInput(algorithms_index, algorithm)
    appData = getAndValidateInput(applications_index, application)
    _, a_data, _ = orderInfo(appData, algData, None)
    endSlash = a_data["separators"][-1]
    
            
    return (endIndex1, endIndex2, endSlash)

def simpleCleanup(paths):
    for preDel in paths:
        if preDel.exists():
            if preDel.is_dir():
                shutil.rmtree(preDel)
            else:
                preDel.unlink()

def cleanup(deletions):
    if(len(deletions) == 0):
        return
    actualDeletions  = toDelete(deletions)
    for deletion in actualDeletions:
        p = Path(deletion)
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
                
def swapCleanup(old, new):
    actualDeletions  = toDelete2(old, new)
    for deletion in actualDeletions:
        p = Path(deletion)
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()

def invert_File(basePath):
    base = Path(basePath)
    paths = getPaths(base)
    deletions = []
    
    for oldpath in paths:
        original = PathingObject(oldpath)
        p = PathingObject(oldpath)
        p.invert(*extractInversionData(p))
        deletions.append(original.findDeletion(p))
        newpath = p.getPath()
        root = p.getRoot()
        root.mkdir(parents=True, exist_ok=True)
        oldpath.replace(newpath)
        
    cleanup(deletions)
        
def addTimestamp_File(paths, joint, default="0000-00-00-00-00-00"):
    first_element = (not joint["use_timestamp"]) and (not joint["use_randID"])
    deletions = []
    for oldpath in paths:
        original = PathingObject(oldpath)
        p = PathingObject(oldpath)
        i0, j0 = p.baseIndices()
        if first_element:
            i = i0
            j = j0
        else:
            i, j = p.getIndex(i0, j0, -1)
            
        p.insert(i, j, default)
        if first_element:
            if joint["sep_after"]:
                i, j = p.getIndex(*p.baseIndices(), -1)
                p.split(i, j)
            i, j = p.getIndex(*p.baseIndices(), -2)
            i2, j2 = p.getIndex(*p.baseIndices(), -1)
            if i == i2:
                p.split(i, j)
        deletions.append(original.findDeletion(p))
        newpath = p.getPath()
        root = p.getRoot()
        root.mkdir(parents=True, exist_ok=True)
        oldpath.replace(newpath)
    
    cleanup(deletions)

def removeTimestamp_File(paths, joint, sep_after):
    last_element = not joint["use_randID"]
    deletions = []
    for oldpath in paths:
        original = PathingObject(oldpath)
        p = PathingObject(oldpath)
        if last_element:
            i, j = p.getIndex(*p.baseIndices(), -1)
        else:
            i, j = p.getIndex(*p.baseIndices(), -2)
        p.remove(i, j)
        if last_element and not sep_after:
            i, _ = p.getIndex(*p.baseIndices(), -1)
            p.join(i)
        deletions.append(original.findDeletion(p))
        newpath = p.getPath()
        root = p.getRoot()
        root.mkdir(parents=True, exist_ok=True)
        oldpath.replace(newpath)
            
    cleanup(deletions)

def toggleTimestamp_File(basePath, appData, algData, 
    joint, default="0000-00-00-00-00-00"):
    base = Path(basePath)
    if joint["use_timestamp"]:
        paths = getPaths(base, appData, algData, 0, default)
        firstData, secondData, _ = orderInfo(appData, algData, joint)
        sep_after = secondData["separators"][-1]
        preDeletions = nonDefaultDeletions(base, firstData, secondData, 0, default)
        simpleCleanup(preDeletions)
                
        removeTimestamp_File(paths, joint, sep_after)
    else:
        paths = getPaths(base, appData, algData)
        addTimestamp_File(paths, joint, default)

def addRandID_File(paths, joint, default="00000000"):
    first_element = (not joint["use_timestamp"]) and (not joint["use_randID"])
    deletions = []
    for oldpath in paths:
        original = PathingObject(oldpath)
        p = PathingObject(oldpath)
        i0, j0 = p.baseIndices()
        if first_element:
            i = i0
            j = j0
        else:
            i, j = p.getIndex(i0, j0, -1)
            j += 1
            
        p.insert(i, j, default)
        if first_element:
            if joint["sep_after"]:
                i, j = p.getIndex(*p.baseIndices(), -1)
                p.split(i, j)
            i, j = p.getIndex(*p.baseIndices(), -2)
            i2, j2 = p.getIndex(*p.baseIndices(), -1)
            if i == i2:
                p.split(i, j)
        deletions.append(original.findDeletion(p))
        newpath = p.getPath()
        root = p.getRoot()
        root.mkdir(parents=True, exist_ok=True)
        oldpath.replace(newpath)
        
    cleanup(deletions)

def removeRandID_File(paths, joint, sep_after):
    last_element = not joint["use_timestamp"]
    deletions = []
    for oldpath in paths:
        original = PathingObject(oldpath)
        p = PathingObject(oldpath)
        i, j = p.getIndex(*p.baseIndices(), -1)
        p.remove(i, j)
        if last_element and not sep_after:
            i, _ = p.getIndex(*p.baseIndices(), -1)
            p.join(i)
            
        deletions.append(original.findDeletion(p))
        newpath = p.getPath()
        root = p.getRoot()
        root.mkdir(parents=True, exist_ok=True)
        oldpath.replace(newpath)
            
    cleanup(deletions)

def toggleRandID_File(basePath, appData, algData, 
    joint, default="00000000"):
    base = Path(basePath)
    if joint["use_randID"]:
        paths = getPaths(base, appData, algData, 1, default)
        
        firstData, secondData, _ = orderInfo(appData, algData, joint)
        sep_after = secondData["separators"][-1]
        preDeletions = nonDefaultDeletions(base, firstData, secondData, 1, default)
        simpleCleanup(preDeletions)
        
        removeRandID_File(paths, joint, sep_after)
    else:
        paths = getPaths(base, appData, algData)
        addRandID_File(paths, joint, default)


def toggleTimeRandBreak_File(basePath, appData, algData, joint):
    base = Path(basePath)
    paths = getPaths(base, appData, algData)
        
    deletions = []
    for oldpath in paths:
        original = PathingObject(oldpath)
        p = PathingObject(oldpath)
        i, j = p.getIndex(*p.baseIndices(), -1)
        if joint["sep_after"]:
            p.join(i)
        else:
            p.split(i, j)
        
        deletions.append(original.findDeletion(p))
        newpath = p.getPath()
        root = p.getRoot()
        root.mkdir(parents=True, exist_ok=True)
        oldpath.replace(newpath)
        
    cleanup(deletions)

def toggleBreak_File(basePath, section, index, data):
    base = Path(basePath)
    last_index = len(data["separators"]) - 1
    if last_index < index or index < 0:
        raise ValueError("Index out of bounds")
        
    
    paths = None
    if section == applications_index:
        paths = getPaths(base,appData=data)
    elif section == algorithms_index:
        paths = getPaths(base,algData=data)
    else:
        raise ValueError("Invalid section number")
        
    check_joints = getCheckJoints(section, index == last_index)
    deletions = []
    
    for oldpath in paths:
        original = PathingObject(oldpath)
        p = PathingObject(oldpath)
        containsTsRand = False
        
        if check_joints:
            containsTsRand = checkJoint(p)
        
        if not containsTsRand:
            if section == applications_index:
                i, j = p.getIndex(*p.appIndices(), index)
            else:
                i, j = p.getIndex(*p.algIndices(), index)
                
            
            if data["separators"][index]:
                p.join(i)
            else:
                p.split(i, j)
            deletions.append(original.findDeletion(p))
            newpath = p.getPath()
            root = p.getRoot()
            root.mkdir(parents=True, exist_ok=True)
            oldpath.replace(newpath)
            
    cleanup(deletions)

def swap_File(basePath, section, index1, index2, data):
    old = dict()
    new = dict()
    base = Path(basePath)
    check_joints = True
    length = len(data["headers"])
    
    if index1 <= 0 or index1 >= length:
        raise ValueError("index 1 out of bounds")
    if index2 <= 0 or index2 >= length:
        raise ValueError("index 2 out of bounds")
    if index1 == index2:
        return
        
    lesser_index = -1
    greater_index = -1
    
    if index1 <= index2:
        lesser_index = index1
        greater_index = index2
    else:
        lesser_index = index2
        greater_index = index1
        
    different_policy = data["separators"][index1] != data["separators"][index2]
    on_boundary = greater_index == (length - 1)
    
    paths = None
    check_joints = getCheckJoints(section, on_boundary) and different_policy
    
    if section == applications_index:
        paths = getPaths(base,appData=data)
    else:
        paths = getPaths(base,algData=data)
        
    
    for oldpath in paths:
        original = PathingObject(oldpath)
        build(old, original.listing)
        p = PathingObject(oldpath)
        containsTsRand = False
        
        if check_joints:
            containsTsRand = checkJoint(p)
        
        if section == applications_index:
            i1, j1 = p.getIndex(*p.appIndices(), lesser_index)
            i2, j2 = p.getIndex(*p.appIndices(), greater_index)
        else:
            i1, j1 = p.getIndex(*p.algIndices(), lesser_index)
            i2, j2 = p.getIndex(*p.algIndices(), greater_index)
            
        temp = p.get(i1, j1)
        p.set(i1, j1, p.get(i2, j2))
        p.set(i2, j2, temp)
        if different_policy:
            if data["separators"][greater_index]:
                p.split(i1, j1)
            else:
                p.join(i1)
                
            if section == applications_index:
                i1, j1 = p.getIndex(*p.appIndices(), lesser_index)
                i2, j2 = p.getIndex(*p.appIndices(), greater_index)
            else:
                i1, j1 = p.getIndex(*p.algIndices(), lesser_index)
                i2, j2 = p.getIndex(*p.algIndices(), greater_index)
            if not containsTsRand:
                if data["separators"][lesser_index]:
                    p.split(i2, j2)
                else:
                    p.join(i2)
                
        build(new, p.listing)
        newpath = p.getPath()
        root = p.getRoot()
        root.mkdir(parents=True, exist_ok=True)
        oldpath.replace(newpath)
        
    swapCleanup(old, new)

def addParam_File(basePath, section, index, default, breakAfter, data):
    deletions = []
    base = Path(basePath)
    length = len(data["headers"])
    
    
    if index <= 0 or index > length:
        raise ValueError("index out of bounds")
        
    on_boundary = index == length
    paths = None
    check_joints = getCheckJoints(section, on_boundary)
    
    if section == applications_index:
        paths = getPaths(base,appData=data)
    else:
        paths = getPaths(base,algData=data)
        
    
    for oldpath in paths:
        original = PathingObject(oldpath)
        p = PathingObject(oldpath)
        containsTsRand = False
        
        if check_joints:
            containsTsRand = checkJoint(p)
        
        if section == applications_index:
            i, j = p.getIndex(*p.appIndices(), index - 1)
            j += 1
        else:
            i, j = p.getIndex(*p.algIndices(), index - 1)
            j += 1
            
        p.insert(i, j, default)
        if not on_boundary or not containsTsRand:
            if breakAfter and not data["separators"][index - 1]:
                p.split(i, j)
            elif (not breakAfter) and data["separators"][index - 1]:
                p.join(i)
            
        if data["separators"][index - 1]:
            p.split(i, j-1)
                
        deletions.append(original.findDeletion(p))
        newpath = p.getPath()
        root = p.getRoot()
        root.mkdir(parents=True, exist_ok=True)
        oldpath.replace(newpath)
        
    cleanup(deletions)

def removeParam_File(basePath, section, default, index, data):
    deletions = []
    base = Path(basePath)
    length = len(data["headers"])
    
    if index <= 0 or index >= length:
        raise ValueError("index out of bounds")
        
    on_boundary = index == (length - 1)
    different_policy = data["separators"][index] != data["separators"][index-1]
    paths = None
    check_joints = getCheckJoints(section, on_boundary)
    
    if section == applications_index:
        paths = getPaths(base, appData=data, defaultIndex=index, defaultValue=default)
        firstData, secondData, _ = orderInfo(data, None, None)
        preDeletions = nonDefaultDeletions(base, firstData, secondData, index, default)
        simpleCleanup(preDeletions)
    else:
        paths = getPaths(base, algData=data, defaultIndex=index, defaultValue=default)
        firstData, secondData, _ = orderInfo(None, data, None)
        preDeletions = nonDefaultDeletions(base, firstData, secondData, index, default)
        simpleCleanup(preDeletions)
        
        
    for oldpath in paths:
        original = PathingObject(oldpath)
        p = PathingObject(oldpath)
        containsTsRand = False
        
        if check_joints:
            containsTsRand = checkJoint(p)
        
        if section == applications_index:
            i0, j0 = p.getIndex(*p.appIndices(), index - 1)
            i, j = p.getIndex(*p.appIndices(), index)
        else:
            i0, j0 = p.getIndex(*p.algIndices(), index - 1)
            i, j = p.getIndex(*p.algIndices(), index)
    
        p.remove(i, j)
        if not (containsTsRand or (not different_policy) or data["separators"][index-1]):
            p.join(i0)
            
        deletions.append(original.findDeletion(p))
        newpath = p.getPath()
        root = p.getRoot()
        root.mkdir(parents=True, exist_ok=True)
        oldpath.replace(newpath)
        
    cleanup(deletions)