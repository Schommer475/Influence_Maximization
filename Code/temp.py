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
    
    algdata = {
"headers":["alg-cmab","trees""ta","at","rocks","wood","water"],
"separators":[True,False,False,False,True,True,True]
}
    appdata = {
	"headers":["app-im","cap","bells","whistles","other"],
	"separators":[False,False,False,False,False]
}
    
    path = Path("hal\\da_alg-yab_y_y_y\\ya_ya_app-dab_b_b_b\\ba_do")
    p = namespace.namespace.PathingObject(path)
    print(p.listing)
    p.split(1,0)
    print(*p.algIndices())
    print(*p.appIndices())
    print(*p.baseIndices())
    print(p.listing)
    
    #print(*namespace.namespace.toDelete([[["ya","ba"],["da","ba"],["doo"]],[["ya","ba"],["da","ba"],["bop"]],[["ya","ba"],["da","ba"],["doo"],["bp","chan"]]]),sep=", ")
    
    #toggleBreak(2, "cmab", 0)
    #addParam(1, "im", "networkType", True, 1, "fb")
    #"""
    #params = ParamSet("im","cmab",[],{"networkType":"fl"},[])
    
    #print(params.getPath("2022-02-21-09-53-46","00000000"))
    #"""