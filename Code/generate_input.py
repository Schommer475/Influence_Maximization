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

def readArgs(argv):
    if len(argv) < 3:
        print("Usage:\n    generate_input.py <input_file> <output_file_name> <options>(optional)")
        print("    valid options:")
        print("        -c    (used to place the generated input file into the "
              "common inputs directory, instead of temporary)")
        print("        -r    (used to make the generated input file more human readable at the cost of file size by"
                  " using an indentation value of 6)")
        return False
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
                return False
            if i > 3:
                for j in range(3,i):
                    if argv[i] == argv[j]:
                        print("Error: Option given multiple times: " + argv[i])
                        return False
                    
        if(commonDir):
            outfile = os.path.join(common_inputs, outfile)
        else:
            outfile = os.path.join(temp_inputs, outfile)

        return {
            readable,
            infile,
            outfile
        }

def extractResultBody(data):
    result = dict()
    for key in data:
        if not key == "applications" and not key == "algorithms":
            result[key] = deepcopy(data[key])
    result["applications"] = []
    result["algorithms"] = []
    result["experiments"] = []
    return result

def expand(specs):
    expanded = []
    discovered = set()
    for spec in specs:
        new_spec = dict()
        for key in spec:
            if not key == "params":
                new_spec[key] = deepcopy(spec[key])
            new_spec["params"] = dict()
            layer = [new_spec]
            params = spec["params"]
            for param in params:
                new_layer = []
                for paramValue in params[param]:
                    for partialSpec in layer:
                        cp = deepcopy(partialSpec)
                        cp["params"][param] = deepcopy(paramValue)
                        new_layer.append(cp)
                layer = new_layer
            
            for completedSpec in layer:
                strVer = toString(completedSpec)
                if strVer not in discovered:
                    discovered.add(strVer)
                    expanded.append(completedSpec)  
    return expanded

def filterValid(specs, type, loadedParams):
    copySpecs = deepcopy(specs)
    keptSpecs = []
    keptSpecsValidated = []

    for index, spec in enumerate(specs):
        try:
            loadedParams[type][spec["name"]].validateSolo(spec)
            keptSpecs.append(copySpecs[index])
            keptSpecsValidated.append(spec)
        except Exception as e:
            print("Warning: A combination under " + type + " does not work. Skipping."
                    + " Error message was: \n    " + str(e))
    if len(keptSpecs) == 0:
        raise ValueError("There were no valid " + type + " configurations.")

    return keptSpecs, keptSpecsValidated

def zipGroups(apps, appsValidated, algs, algsValidated, globals, loadedParams, modules, backup):
    appCounts = [0 for _ in apps]
    algCounts = [0 for _ in algs]
    pairs = []
    validPair = False

    gcheck = False
    if (hasattr(loadedParams["globals"],"doFullCheck") and 
        (type(loadedParams["globals"].doFullCheck) is bool)):
        gcheck = loadedParams["globals"].doFullCheck

    for appIndex, app in enumerate(appsValidated):
        for algIndex, alg in enumerate(algsValidated):
            apcheck = False
            alcheck = False
            
            if (hasattr(loadedParams["applications"][app["name"]],"doFullCheck") and 
                (type(loadedParams["applications"][app["name"]].doFullCheck) is bool)):
                apcheck = loadedParams["applications"][app["name"]].doFullCheck
                
            if (hasattr(loadedParams["algorithms"][alg["name"]],"doFullCheck") and 
                (type(loadedParams["algorithms"][alg["name"]].doFullCheck) is bool)):
                alcheck = loadedParams["algorithms"][alg["name"]].doFullCheck
            
            addIt = True
            if gcheck or apcheck or alcheck:
                g = BaseParamSet("",deepcopy(globals)
                    ,backup["globals"])
                ap = BaseParamSet(app["name"]
                            , deepcopy(app["params"])
                            ,backup["applications"][app["name"]])
                al = BaseParamSet(alg["name"]
                            , deepcopy(alg["params"])
                            ,backup["algorithms"][alg["name"]])
                params = ParamSet(g, ap, al)
                application = modules["application"][app["name"]].createInstance(ap)
                algorithm = modules["algorithm"][alg["name"]].createInstance(al)
                
                if gcheck:
                    try:
                        loadedParams["globals"].validateFull(params, application, algorithm)
                    except Exception as e:
                        print("Warning: The combination of the following does not work for globals. Skipping.\n"+
                        "Application: " + toString(app) + "\n"+
                        "Algorithm: " + toString(alg) + "\n"+
                        "Error message was: \n    " + str(e))
                        addIt = False
                        
                if apcheck and addIt:
                    try:
                        loadedParams["applications"][app["name"]].validateFull(params, application, algorithm)
                    except Exception as e:
                        print("Warning: The combination of the following does not work for applications. Skipping.\n"+
                        "Application: " + toString(app) + "\n"+
                        "Algorithm: " + toString(alg) + "\n"+
                        "Error message was: \n    " + str(e))
                        addIt = False
                if alcheck and addIt:
                    try:
                        loadedParams["algorithms"][alg["name"]].validateFull(params, application ,algorithm)
                    except Exception as e:
                        print("Warning: The combination of the following does not work for algorithms. Skipping.\n"+
                        "Application: " + toString(app) + "\n"+
                        "Algorithm: " + toString(alg) + "\n"+
                        "Error message was: \n    " + str(e))
                        addIt = False
            
            if addIt:
                appCounts[appIndex] += 1
                algCounts[algIndex] += 1
                validPair = True
                pairs.append({
                    application: appIndex,
                    algorithm: algIndex
                })

    if not validPair:
        raise ValueError("There were no valid application/algorithm pairs generated.")

    appMappings = [0 for _ in apps]
    algMappings = [0 for _ in algs]
    applications = []
    algorithms = []
    appCount = 0
    algCount = 0

    for index, count in enumerate(appCounts):
        if count != 0:
            appMappings[index] = appCount
            appCount += 1
            applications.append(apps[index])
        else:
            print("Warning: There are no valid use cases found for the following applications" + 
                    + " entry. Skipping. " + toString(apps[index]))

    for index, count in enumerate(algCounts):
        if count != 0:
            algMappings[index] = algCount
            algCount += 1
            algorithms.append(algs[index])
        else:
            print("Warning: There are no valid use cases found for the following algorithms" + 
                    + " entry. Skipping. " + toString(apps[index]))

    experiments = []

    for pair in pairs:
        experiments.append({
            application: appMappings[pair.application],
            algorithm: algMappings[pair.algorithm]
        })

    return applications, algorithms, experiments


def main(argv):
    argResults = readArgs(argv)

    if not argResults:
        return

    data = None
    with open(argResults.infile, "r") as f:
        data  = json.load(f)
        
    validateInput(data, True)
    result = extractResultBody(data)
    applications = expand(data.applications)
    algorithms = expand(data.algorithms)
    
    loadedParams, modules, backup = loadModules(listModules({
        applications,
        algorithms
    }))
    
    globals = deepcopy(result.global_vars)
    loadedParams["globals"].validateSolo(globals)
    applications, validatedApplications = filterValid(applications, "applications", loadedParams)
    algorithms, validatedAlgorithms = filterValid(algorithms, "algorithms", loadedParams)
                
    applications, algorithms, experiments = zipGroups(
        applications,
        validatedApplications,
        algorithms,
        validatedAlgorithms,
        globals,
        loadedParams,
        modules,
        backup
    )

    result.applications = applications
    result.algorithms = algorithms
    result.experiments = experiments
    
    with open(argResults.outfile, "w") as f:
        if argResults.readable:
            json.dump(result, f, indent=6)
        else:
            json.dump(result, f)
            
    print("Complete. Generated output file: " + argResults.outfile)
        

if __name__=="__main__":
    main(sys.argv)
        
        