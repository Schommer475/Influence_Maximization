# -*- coding: utf-8 -*-
"""
Created on Wed May 11 19:47:41 2022

@author: Tim Schommer
"""

num_choices = 10

def validateSolo(dat):
    data = dat["params"]
    if "num_choices" in data:
        val = data["num_choices"]
        if type(val) is not int or val < 1:
            raise AttributeError("The field 'num_choices' must be an"
                                " integer with value at least 1")