#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 21:49:19 2019

@author: abhishek.umrawal
"""
import pickle as pickle

fname = 'results/output_cmab__0.10__2__5000__03332798.pkl'
with open(fname, 'rb') as f:
    tmpdict = pickle.load(f)

list( tmpdict.keys() ) 