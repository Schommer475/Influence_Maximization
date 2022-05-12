# -*- coding: utf-8 -*-
"""
Created on Wed May 11 21:06:32 2022

@author: raqua
"""
import numpy as np

if __name__ == "__main__":
    x = ['a', 'b', 'c']

    mask = np.array([True, False, True])
    x_arr = np.asarray(x, dtype=object)
    output = x_arr[mask]  # Get items
    x_arr[mask] = ['new', 'values']  # Set items
    print(output)