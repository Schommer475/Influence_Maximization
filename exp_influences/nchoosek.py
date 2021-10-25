#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 16:58:05 2019

@author: abhishek.umrawal
"""
import copy
import numpy as np

def nchoosek(N, K):
        #import copy
        actions = []
        def printCombination(arr, n, r): 
            data = [0]*r; 
            combinationUtil(arr, data, 0, n - 1, 0, r); 

        def combinationUtil(arr, data, start, end, index, r): 
            if (index == r): 
        #         print(data, end = "\n"); 
                act = copy.deepcopy(data)
                actions.append(act)
                return; 

            i = start; 
            while(i <= end and end - i + 1 >= r - index): 
                data[index] = arr[i]; 
                combinationUtil(arr, data, i + 1, end, index + 1, r); 
                i += 1; 

        # Driver Code 
        arr = np.arange(N)+1; 
        r = K; 
        n = len(arr); 
        printCombination(arr, n, r); 
        return actions
