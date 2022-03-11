# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 13:34:37 2022

@author: raqua
"""

from parameters.parameterization import ParamSet
import namespace.namespace
from Utilities.global_names import global_namespace, application_namespace,\
    algorithm_namespace, joint_namespace, temp_dir
import os.path
from pathlib import Path


        
        
if __name__ == "__main__":
    ts = "2022-10-24-14-54-33"
    rand = "1234567"
    
    alg3 = {
"headers":["alg-o3","trees","ta","at","rocks","wood"],
"separators":[False,False,False,False,True,True]
}
    alg4 = {
"headers":["alg-o4","trees","ta","at","rocks","wood"],
"separators":[False,False,False,False,False,True]
}
    alg5 = {
"headers":["alg-o5","trees","ta","at","rocks","wood"],
"separators":[False,False,False,False,False,True]
}
    alg6 = {
"headers":["alg-o6","trees","ta","at","rocks","wood"],
"separators":[False,False,False,False,True,False]
}
    alg7 = {
"headers":["alg-o7","trees","ta","at","rocks","wood"],
"separators":[False,False,False,False,False,False]
}
    alg8 = {
"headers":["alg-o8","trees,""ta","at","rocks","wood"],
"separators":[False,False,False,False,False,False]
}
    app1 = {
	"headers":["app-o1","cap","bells","whistles","other","ha"],
	"separators":[True,False,False,False,False,True]
}
    
    app2 = {
	"headers":["app-o2","cap","bells","whistles","other","ha"],
	"separators":[True,False,False,False,False,False]
}
    
    #namespace.namespace.invert()
    #namespace.namespace.removeParam_File(temp_dir, 2, "d1", 5, alg3)
    #namespace.namespace.removeParam(1,"o1",2,"d")
    namespace.namespace.toggleBreak(2, "o3", 2)
    namespace.namespace.toggleBreak(2, "o3", 3)
    #namespace.namespace.swap(2, "o3", 2, 3)
    #namespace.namespace.addParam(1,"o1","c",False,3,"d")
    #namespace.namespace.toggleBreak_File(temp_dir, 2, 4, alg3)
    #namespace.namespace.toggleBreak_File(temp_dir, 2, 4, alg6)
    #namespace.namespace.toggleTimeRandBreak_File(temp_dir, app1, alg4, joint)
    #namespace.namespace.toggleTimestamp_File(temp_dir, app2, alg7, joint, default="d")
    