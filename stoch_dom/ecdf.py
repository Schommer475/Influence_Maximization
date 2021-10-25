#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 30 06:37:40 2020

@author: root
"""
import numpy as np

def ecdf(data, num_bins=10, bins=[]):
    data = sorted(data)
    if len(bins) == 0:
        bins = list(np.linspace(min(data),max(data),num_bins))
    counts = [0]*len(bins)
    for i,b in enumerate(bins):
        for val in data:
            if val <= bins[i]:
                counts[i]+=1
    return bins, [1-count/counts[-1] for count in counts]
    
