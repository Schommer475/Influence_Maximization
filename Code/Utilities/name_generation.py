# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 13:41:04 2022

@author: Tim Schommer
"""

import datetime
import random

def getTimestamp():
    return '{:%Y-%m-%d-%H-%M-%S}'.format(datetime.datetime.now())

def getRandomId():
    ID = ''
    for i in range(8):
        ID += str(random.randint(0,9))
    return ID
