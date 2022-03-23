# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 13:34:37 2022

@author: raqua
"""

from parameters.parameterization import readInFile

from multiprocessing import Pool
import os.path

def doIt(a):
    return a.getPath("2022-03-20-12-16-59","12345678")

        
if __name__ == "__main__":
    print(readInFile("../Files/Inputs/temp/test_input.json"))
    
    
    
        