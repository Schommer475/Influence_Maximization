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
"headers":["alg-o3","trees""ta","at","rocks","wood"],
"separators":[False,False,False,False,False,True]
}
    alg4 = {
"headers":["alg-o4","trees""ta","at","rocks","wood"],
"separators":[False,False,False,False,False,True]
}
    alg5 = {
"headers":["alg-o5","trees""ta","at","rocks","wood"],
"separators":[False,False,False,False,False,True]
}
    alg6 = {
"headers":["alg-o6","trees""ta","at","rocks","wood"],
"separators":[False,False,False,False,False,False]
}
    alg7 = {
"headers":["alg-o7","trees""ta","at","rocks","wood"],
"separators":[False,False,False,False,False,False]
}
    alg8 = {
"headers":["alg-o8","trees""ta","at","rocks","wood"],
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
    
    base = Path(temp_dir)
    joint = {"use_timestamp":False,"use_randID":True,"sep_after":True}
    paths = namespace.namespace.getPaths(base, app2, alg7, 1, "d")
    """
    base = Path(temp_dir)
    paths = namespace.namespace.getPaths(base, appData=app2, algData=alg7,defaultIndex=0,defaultValue="f")
    
    for p in paths:
        print(p)
        
    path1 = Path(os.path.join(temp_dir,"app-o1","n_n_n_n_n","alg-o3_n_n_d_n_n","file.txt"))
    path2 = Path(os.path.join(temp_dir,"app-o1","n_n_d_n_n","alg-o5_n_n_d_n_n"))
    namespace.namespace.simpleCleanup([path2])"""
    
    #namespace.namespace.removeRandID_File(paths, joint, alg7["separators"][-1])
    namespace.namespace.toggleTimeRandBreak_File(temp_dir, app1, alg4, joint)
    #namespace.namespace.toggleTimestamp_File(temp_dir, app2, alg7, joint, default="d")
    
    #toggleBreak(2, "cmab", 0)
    #addParam(1, "im", "networkType", True, 1, "fb")
    #"""
    #params = ParamSet("im","cmab",[],{"networkType":"fl"},[])
    
    #print(params.getPath("2022-02-21-09-53-46","00000000"))
    #"""