# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 20:08:02 2022

@author: Tim Schommer
"""
import random
import numpy
import json
import sys
from parameters.parameterization import readInFile
from Utilities.global_names import logging
from Utilities.name_generation import getTimestamp, getRandomId
import os.path
import multiprocessing as mp
import pickle

class Outputer:
    def __init__(self, fname):
        self.fname = fname
        
    def put(self, value):
        if value == "kill":
            return
        
        data = None
        with open(self.fname, 'r') as f:
            data = json.load(f)
        with open(self.fname, 'w') as f:
            data[str(value)] = True
            json.dump(data, f)
            f.flush()
            
    
    
def worker(seed, queue, expwrapper, refresh):
    random.seed(seed)
    numpy.random.seed(random.randint(0, 2**32 - 1))
    r = getRandomId()
    ts = getTimestamp()
    params, application, algorithm = expwrapper.get(refresh)
    ret = algorithm.run(application,params, ts, r)
    if ret is None:
        ret = dict()
    output = {"params":params,"results":ret}
    pth = params.getPath(ts,r)
    fullpath = pth + "results.pkl"
    params.reset()
        
    with open(fullpath, "wb") as f:
        pickle.dump(output, f)
    queue.put(seed)
    
def listener(file, q):
    data = None
    with open(file, 'r') as f:
        data = json.load(f)
    
    while 1:
        m = q.get()
        if m == "kill":
            break
        data[str(m)] = True
        with open(file, 'w') as f:
            json.dump(data, f)
            f.flush()
            
            
if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Usage:\n    run_experiment.py <input_file> <options>(optional)")
        print("    valid options:")
        print("        -s seed    (used to run experiment set with a given starting seed)")
    else:
        infile = sys.argv[1]
        seed = None
        if len(sys.argv) >= 4 and sys.argv[2] == "-s":
            seed = int(sys.argv[3])
        else:
            seed = random.randint(0, 2**32 - 1)
            
        print("Run id is: " + str(seed))
        random.seed(seed)
        numpy.random.seed(random.randint(0, 2**32 - 1))
        globs, runs = readInFile(infile)
        print("Finished setup")
        
        data = None
        pth = os.path.join(logging, str(seed) + ".json")
        if not os.path.exists(pth):
            if not os.path.exists(logging):
                os.mkdir(logging)
            data = dict()
        else:
            with open(pth, "r") as f:
                data = json.load(f)
                
        toRun = []
        newKeys = set()
        num_runs = globs.get("num_runs")
        for i in range(len(runs)):
            for j in range(num_runs):
                sd = random.randint(0, 2**32 - 1)
                while sd in newKeys:
                    sd = random.randint(0, 2**32 - 1)
                newKeys.add(sd)
                key = str(sd)
                if key not in data:
                    data[key] = False
                if not data[key]:
                    toRun.append((sd, runs[i]))
                
        with open(pth,"w") as f:
            json.dump(data, f, indent=6)
            f.flush()
        
        cores = globs.get("num_cores")
        doRefresh = globs.get("refresh")
        globs.reset()
        print("running")
        
        if cores < 3:
            q = Outputer(pth)
            for _seed, exp in toRun:
                worker(_seed, q, exp, doRefresh)
        else:
            manager = mp.Manager()
            q = manager.Queue()    
            pool = mp.Pool(cores)
        
            #put listener to work first
            watcher = pool.apply_async(listener, (pth,q))
            
            #fire off workers
            jobs = []
            for _seed, exp in toRun:
                job = pool.apply_async(worker, (_seed, q, exp, doRefresh))
                jobs.append(job)
        
            # collect results from the workers through the pool result queue
            for job in jobs: 
                job.get()
        
            #now we are done, kill the listener
            q.put('kill')
            pool.close()
            pool.join()
        
        print("experiments complete")
        
        