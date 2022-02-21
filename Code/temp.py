# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 13:34:37 2022

@author: raqua
"""

from parameters.parameterization import ParamSet
from namespace.namespace import invert, addParam, toggleBreak



        
        
if __name__ == "__main__":
    toggleBreak(2, "cmab", 0)
    #addParam(1, "im", "networkType", True, 1, "fb")
    """
    params = ParamSet("im","cmab",[],{"networkType":"fl"},[])
    print(params.getPath("2022-02-21-09-53-46","00000000"))
    """