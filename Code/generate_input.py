# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 11:55:37 2022

@author: Tim Schommer
"""
import sys
import os.path
import json
from Utilities.global_names import temp_inputs, common_inputs
from parameters.parameterization import validateInput, listModules, loadModules\
    , BaseParamSet, ParamSet
from copy import deepcopy

def toString(item):
    if type(item) is dict:
        out = "{"
        keys = sorted(item.keys())
        if len(keys) > 0:
            out += keys[0] + ":" + toString(item[keys[0]])
        for i in range(1,len(keys)):
            out += ", " + keys[i] + ":" + toString(item[keys[i]])
        out += "}"
        return out
    elif type(item) is list:
        out = "["
        if len(item) > 0:
            out += toString(item[0])
        for i in range(1,len(item)):
            out += ", " + toString(item[i])
        out += "]"
        return out
    else:
        return str(item)

def main(argv):
    if len(argv) < 3:
        print("Usage:\n    generate_input.py <input_file> <output_file_name> <options>(optional)")
        print("    valid options:")
        print("        -c    (used to place the generated input file into the "
              "common inputs directory, instead of temporary)")
        print("        -r    (used to make the generated input file more human readable at the cost of file size by"
                  " using an indentation value of 6)")
    else:
        infile = argv[1]
        outfile = argv[2]
        if not os.path.exists(infile):
            print("Error: The given input file does not exist.")
            return
        if not outfile.endswith(".json"):
            outfile += ".json"
        
        commonDir = False
        readable = False
        for i in range(3,len(argv)):
            if argv[i] == "-c":
                commonDir = True
            elif argv[i] == "-r":
                readable = True
            else:
                print("Error: Unrecognized option: " + argv[i])
                return
            if i > 3:
                for j in range(3,i):
                    if argv[i] == argv[j]:
                        print("Error: Option given multiple times: " + argv[i])
                        return
                    
        if(commonDir):
            outfile = os.path.join(common_inputs, outfile)
        else:
            outfile = os.path.join(temp_inputs, outfile)
        data = None
        with open(infile, "r") as f:
            data  = json.load(f)
            
        validateInput(data, False)
        result = dict()
        for key in data:
            if not key == "applications" and not key == "algorithms":
                result[key] = deepcopy(data[key])
        result["applications"] = []
        result["algorithms"] = []
        
        for i in ["applications", "algorithms"]:
            discovered = set()
            for a in data[i]:
                new_a = dict()
                for key in a:
                    if not key == "params":
                        new_a[key] = deepcopy(a[key])
                new_a["params"] = dict()
                layer = [new_a]
                par = a["params"]
                for p in par:
                    new_layer = []
                    for item in par[p]:
                        for cumulative in layer:
                            cp = deepcopy(cumulative)
                            cp["params"][p] = deepcopy(item)
                            new_layer.append(cp)
                    layer = new_layer
                
                for item in layer:
                    strVer = toString(item)
                    if strVer not in discovered:
                        discovered.add(strVer)
                        result[i].append(item)
        
        loadedParams, modules, backup = loadModules(listModules(result))
        
        data = deepcopy(result)
        temp = {"applications":[],"algorithms":[]}
        temp2 = {"applications":[],"algorithms":[]}
        loadedParams["globals"].validateSolo(data["global_vars"])
        for i in ["applications", "algorithms"]:
            for num, dat in enumerate(data[i]):
                try:
                    loadedParams[i][dat["name"]].validateSolo(dat)
                    t = result[i][num]
                    t["uses"] = []
                    temp[i].append(result[i][num])
                    temp2[i].append(dat)
                except Exception as e:
                    print("Warning: A combination under " + i + " does not work. Skipping."
                          + " Error message was: \n    " + str(e))
            if len(temp[i]) == 0:
                raise ValueError("There were no valid " + i + " configurations.")
                    
        
                    
        count = 0
        for n1, app in enumerate(temp2["applications"]):
            for n2, alg in enumerate(temp2["algorithms"]):
                gcheck = False
                apcheck = False
                alcheck = False
                if (hasattr(loadedParams["globals"],"doFullCheck") and 
                    (type(loadedParams["globals"].doFullCheck) is bool)):
                    gcheck = loadedParams["globals"].doFullCheck
                
                if (hasattr(loadedParams["applications"][app["name"]],"doFullCheck") and 
                    (type(loadedParams["applications"][app["name"]].doFullCheck) is bool)):
                    apcheck = loadedParams["applications"][app["name"]].doFullCheck
                    
                if (hasattr(loadedParams["algorithms"][alg["name"]],"doFullCheck") and 
                    (type(loadedParams["algorithms"][alg["name"]].doFullCheck) is bool)):
                    alcheck = loadedParams["algorithms"][alg["name"]].doFullCheck
                
                addIt = True
                if gcheck or apcheck or alcheck:
                    g = BaseParamSet("",deepcopy(data["global_vars"])
                     ,backup["globals"])
                    ap = BaseParamSet(app["name"]
                                , deepcopy(app["params"])
                                ,backup["applications"][app["name"]])
                    al = BaseParamSet(alg["name"]
                                , deepcopy(alg["params"])
                                ,backup["algorithms"][alg["name"]])
                    p = ParamSet(g, ap, al)
                    appl = modules["application"][app["name"]].createInstance(ap)
                    algo = modules["algorithm"][alg["name"]].createInstance(al)
                    
                    if gcheck:
                        try:
                            loadedParams["globals"].validateFull(p,appl,algo)
                        except Exception as e:
                            print("Warning: The combination of the following does not work for globals. Skipping.\n"+
                          "Application: " + toString(app) + "\n"+
                          "Algorithm: " + toString(alg) + "\n"+
                          "Error message was: \n    " + str(e))
                            addIt = False
                            
                    if apcheck and addIt:
                        try:
                            loadedParams["applications"][app["name"]].validateFull(p,appl,algo)
                        except Exception as e:
                            print("Warning: The combination of the following does not work for applications. Skipping.\n"+
                          "Application: " + toString(app) + "\n"+
                          "Algorithm: " + toString(alg) + "\n"+
                          "Error message was: \n    " + str(e))
                            addIt = False
                    if alcheck and addIt:
                        try:
                            loadedParams["algorithms"][alg["name"]].validateFull(p,appl,algo)
                        except Exception as e:
                            print("Warning: The combination of the following does not work for algorithms. Skipping.\n"+
                          "Application: " + toString(app) + "\n"+
                          "Algorithm: " + toString(alg) + "\n"+
                          "Error message was: \n    " + str(e))
                            addIt = False
                
                if addIt:
                    temp["applications"][n1]["uses"].append(count)
                    temp["algorithms"][n2]["uses"].append(count)
                    count += 1
                    
        if count == 0:
            raise ValueError("There were no valid application/algorithm pairs generated.")
        
        result["num_experiments"] = count
        t = {"applications":[],"algorithms":[]}
        for i in ["applications", "algorithms"]:
            for item in temp[i]:
                if len(item["uses"]) == 0:
                    print("Warning: There are no valid use cases found for the following " + 
                          i + " entry. Skipping. " + toString(item))
                else:
                    new_uses = []
                    start = item["uses"][0]
                    end = -1
                    for j in range(1,len(item["uses"])):
                        num = item["uses"][j]
                        if end == -1:
                            if num == start + 1:
                                end = num
                            else:
                                new_uses.append(start)
                                start = num
                        else:
                            if num == end + 1:
                                end = num
                            else:
                                new_uses.append(str(start)+"-"+str(end))
                                start = num
                                end = -1
                    if end == -1:
                        new_uses.append(start)
                    else:
                        new_uses.append(str(start)+"-"+str(end))
                        
                    item["uses"] = new_uses
                    t[i].append(item)
                    
        for i in ["applications", "algorithms"]:
            result[i] = t[i]
        
        with open(outfile, "w") as f:
            if readable:
                json.dump(result, f, indent=6)
            else:
                json.dump(result, f)
                
        print("Complete. Generated output file: " + outfile)
        

if __name__=="__main__":
    main(sys.argv)
        
        