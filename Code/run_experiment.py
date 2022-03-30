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
import os.path
import multiprocessing as mp

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
            
    
    
def worker(seed, queue, params, application, algorithm):
    random.seed(seed)
    numpy.random.seed(random.randint(0, 2**32 - 1))
    algorithm.run(application,params)
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
        for i in range(len(runs)):
            sd = random.randint(0, 2**32 - 1)
            while sd in newKeys:
                sd = random.randint(0, 2**32 - 1)
            newKeys.add(sd)
            key = str(sd)
            if key not in data:
                data[key] = False
            if not data[key]:
                toRun.append((sd,*runs[i]))
                
        with open(pth,"w") as f:
            json.dump(data, f, indent=6)
            f.flush()
        
        cores = globs.get("num_cores")
        print("running")
        
        if cores < 3:
            q = Outputer(pth)
            for _seed, par, ap, al in toRun:
                worker(_seed, q, par, ap, al)
        else:
            manager = mp.Manager()
            q = manager.Queue()    
            pool = mp.Pool(cores)
        
            #put listener to work first
            watcher = pool.apply_async(listener, (pth,q))
            
            #fire off workers
            jobs = []
            for _seed, par, ap, al in toRun:
                job = pool.apply_async(worker, (_seed, q, par, ap, al))
                jobs.append(job)
        
            # collect results from the workers through the pool result queue
            for job in jobs: 
                job.get()
        
            #now we are done, kill the listener
            q.put('kill')
            pool.close()
            pool.join()
        
        print("experiments complete")
        
        