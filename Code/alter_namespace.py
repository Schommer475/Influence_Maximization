# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 14:43:51 2022

@author: Tim Schommer
"""
import sys
from sys import exit
from namespace import namespace
from Utilities.program_vars import applications_index, algorithms_index, joint_index
"""
Invert           fixed mode

TS              fixed mode;  app/alg specifying with "all" options; defaults
Rand            fixed mode;  app/alg specifying with "all" options; defaults
Break after     fixed mode;  app/alg specifying with "all" options

Swapping        by index or param name; identify app/alg
Break on param  by index or param name; fixed mode; identify app/alg
Insert param    part to insert before by index or value; default val; identify app/alg; name; sep(optional)
remove param    by index or param name; default val; identify app/alg

Information on app/alg/joint      individual or "all" mode
list all application/algorithms/both

register app/alg
deregister app/alg


"""
appNumber = applications_index
algNumber = algorithms_index
fixedNumber = None
defaultNumber = None
basicNumber = None
atNumber = None
mode2Number = None
sepNumber = None

def doAssign():
    assigned = 0
    i = 0
    global appNumber 
    global algNumber 
    global jointNumber
    global fixedNumber 
    global defaultNumber 
    global basicNumber 
    global atNumber
    global mode2Number
    global sepNumber
    toAssign = [0,0,0,0,0,0]
    while assigned < 6:
        if not (i == appNumber or i == algNumber):
            toAssign[assigned] = i
            assigned += 1
        i += 1
    
    fixedNumber = toAssign[0]
    defaultNumber = toAssign[1]
    basicNumber = toAssign[2]
    atNumber = toAssign[3]
    mode2Number = toAssign[4]
    sepNumber = toAssign[5]

doAssign()


trueAlias = ["true", "True"]
trueGroup = (trueAlias, True)
falseAlias = ["false", "False"]
falseGroup = (falseAlias, False)
leftAppAlias = ["--app="]
leftAlgAlias = ["--alg="]
baseRightApp = ["app", "1"]
baseRightAlg = ["alg", "2"]
baseRightJoint = ["both", "3"]
appGroup = (leftAppAlias, appNumber)
algGroup = (leftAlgAlias, algNumber)

baseAppGroup = (baseRightApp, applications_index)
baseAlgGroup = (baseRightAlg, algorithms_index)
baseJointGroup = (baseRightJoint, joint_index)

fixedArg = ((["--fixed="],fixedNumber),[trueGroup, falseGroup])
algSpecifier = (algGroup,True)
appSpecifier = (appGroup,True)
defaultSpecifier = ((["--default="],defaultNumber),True)
basicSpecifier = ((True, basicNumber), True)
atSpecifier = ((["--at="],atNumber),True)
mode2Specifier = ((True, mode2Number), [baseAppGroup, baseAlgGroup, baseJointGroup])
sepSpecifier = ((["--sep="],sepNumber),[trueGroup, falseGroup])

def identifyArg(arg, specifications):
    allowBasic = False
    allowMode2 = False
    modeRight = None
    for spec in specifications:
        left, right = spec
        vals, number = left
        if type(vals) is bool and number == basicNumber:
            allowBasic = True
            continue
        elif type(vals) is bool:
            allowMode2 = True
            modeRight = right
            continue
        for v in vals:
            if arg.startswith(v):
                if len(arg) == len(v):
                    print("No value passed with '" + arg + "' parameter. Run without arguments to see usage details.")
                    exit(1)
                if type(right) is bool:
                    return (number, arg[len(v):])
                else:
                    temp = arg[len(v):]
                    for group in right:
                        options, groupVal = group
                        for option in options:
                            if temp == option:
                                return (number, groupVal)
                    print("Invalid value passed with 'fixed' parameter. Run without arguments to see usage details.")
                    exit(1)
    if allowMode2:
        for group in modeRight:
            options, groupVal = group
            for option in options:
                if arg == option:
                    return (mode2Number, groupVal)
    if allowBasic:
        return (basicNumber, arg)
    
    print("Arg '" + arg + "' is not valid for the given mode. Run without arguments to see usage details.")
    exit(1)
    
def identifyDuplicates(args, maxBasics=0):
    basicCount = 0
    types = set()
    for arg in args:
        number, _ = arg
        if number == basicNumber:
            if basicCount >= maxBasics:
                print("Too many non-flag arguments for swap operation. Run without arguments to see usage details.")
                exit(1)
            basicCount += 1
        else:
            if number in types:
                p1 = "Multiple instances of the '"
                p2 = "' argument given. Run without arguments to see usage details."
                if number == appNumber:
                    print(p1 + "--app=<application name>" + p2)
                elif number == algNumber:
                    print(p1 + "--alg=<algorithm name>" + p2)
                elif number == fixedNumber:
                    print(p1 + "--fixed=<bool>" + p2)
                elif number == defaultNumber:
                    print(p1 + "--default=<value>" + p2)
                elif number == atNumber:
                    print(p1 + "--at=<value>" + p2)
                elif number == mode2Number:
                    print(p1 + "<listing Mode>" + p2)
                elif number == sepNumber:
                    print(p1 + "--sep=<bool>" + p2)
                exit(1)
            types.add(number)
        
def orderArgs(args):
    ordered = [None,None,None,None,None,None,None,None,None]
    basicCount = 0
    for arg in args:
        number = arg[0]
        if number == appNumber:
            ordered[0] = arg[1]
        elif number == algNumber:
            ordered[1] = arg[1]
        elif number == fixedNumber:
            ordered[2] = arg[1]
        elif number == defaultNumber:
            ordered[3] = arg[1]
        elif number == basicNumber:
            ordered[4 + basicCount] = arg[1]
            basicCount += 1
        elif number == atNumber:
            ordered[6] = arg[1]
        elif number == mode2Number:
            ordered[7] = arg[1]
        elif number == sepNumber:
            ordered[8] == arg[1]
            
    return ordered

def processArgs(args, specifications, maxBasics=0):
    ret = []
    for arg in args:
        ret.append(identifyArg(arg, specifications))
    identifyDuplicates(ret, maxBasics)
    
    return orderArgs(ret)


groups = {
      "-invert":0, "-0":0,
      "-timestamp":1, "-1":1,
      "-randId":2, "-2":2,
      "-joint-break":3, "-3":3,
      "-swap":4, "-4":4,
      "-break":5,"-5":5,
      "-add":6, "-6":6,
      "-remove":7, "-7":7,
      "-info":8, "-8":8,
      "-list":9, "-9":9,
      "-register":10,"-10":10,
      "-unregister":11, "-11":11
      }


def getMode(val):
    if val in groups:
        return groups[val]
        
    return -1
    
def printUsage():
    usage = ("Usage:\n"
        +"    alter_namespace.py -<mode> [relevant arguments (see individual modes for which argument\n"
        +"                                  types are possibly relevant)]\n"
        +"    Note 1: Modes can be called using either their name or their number.\n"
        +"            For instance, the invert mode can be called with either -invert or -0\n"
        +"    Note 2: After mode, arguments can appear in any order.\n\n"
        +"    Valid modes: (number) name\n"
        +"        (0) invert\n"
        +"                Changes whether it is the applications or the algorithms that appear\n"
        +"                first in file paths. Existing file paths are rearranged.\n"
        +"            Relevant arguments:\n"
        +"                *(optional) <value>\n"
        +"                     Indicates whether you want the applications or algorithms to be first\n"
        +"                     in the the file paths. If left out, it will simply be changed from\n"
        +"                     whatever it is at currently.\n"
        +"                     Valid values are: app or 1 to indicate that applications should be first\n"
        +"                                 and alg or 2 to indicate that algorithms should be first.\n"
        +"        (1) timestamp\n"
        +"                Either adds or removes a timestamp to/from the file path of the experiments\n"
        +"                that fall under the application-algorithm pair(s) indicated by the arguments.\n"
        +"            Relevant arguments:\n"
        +"                *--app=<value>\n"
        +"                     Indicates the application(s) part of the application-algorithm pair(s) for\n"
        +"                     which the presence of a timestamp should be changed.\n"
        +"                     Value should be either the name of the application or -all\n"
        +"                     If the value is -all, every algorithm indicated by the --alg argument will\n"
        +"                     be paired with every application registered in the namespace system's list\n"
        +"                     of all applications.\n"
        +"                     Note that, while you do not need it to be registered to operate on an\n"
        +"                     individual application, it will need to be registered to be brought up\n"
        +"                     using -all.\n"
        +"                *--alg=<value>\n"
        +"                     Indicates the algorithm(s) part of the application-algorithm pair(s) for\n"
        +"                     which the presence of a timestamp should be changed.\n"
        +"                     Value should be either the name of the algorithm or -all\n"
        +"                     If the value is -all, every application indicated by the --app argument will\n"
        +"                     be paired with every algorithm registered in the namespace system's list\n"
        +"                     of all applications.\n"
        +"                     Note that, while you do not need it to be registered to operate on an\n"
        +"                     individual algorithm, it will need to be registered to be brought up\n"
        +"                     using -all.\n"
        +"                *--default=<value>\n"
        +"                     When adding a timestamp, this is the value to be used as the timestamp for all\n"
        +"                     already existing experiments that are affected.\n"
        +"                     When removing a timestamp, experiments in the affected paths that have this\n"
        +"                     timestamp will be kept, all others will be discarded.\n"
        +"                *(optional) --fixed=<value>\n"
        +"                     This is used to ensure that timestamp usage will be the same for every\n"
        +"                     application-algorithm pair indicated by the arguments. Pairs that already\n"
        +"                     match the desired setting will be skipped.\n"
        +"                     If this argument is left off, every indicated pair will change whether\n"
        +"                     or not it is using a timestamp.\n"
        +"                     Valid values are true to use a timestamp or false to not use a timestamp.\n"
        +"        (2) randId\n"
        +"                Either adds or removes a random ID to/from the file path of the experiments\n"
        +"                that fall under the application-algorithm pair(s) indicated by the arguments.\n"
        +"            Relevant arguments:\n"
        +"                *--app=<value>\n"
        +"                     Indicates the application(s) part of the application-algorithm pair(s) for\n"
        +"                     which the presence of a random ID should be changed.\n"
        +"                     Value should be either the name of the application or -all\n"
        +"                     If the value is -all, every algorithm indicated by the --alg argument will\n"
        +"                     be paired with every application registered in the namespace system's list\n"
        +"                     of all applications.\n"
        +"                     Note that, while you do not need it to be registered to operate on an\n"
        +"                     individual application, it will need to be registered to be brought up\n"
        +"                     using -all.\n"
        +"                *--alg=<value>\n"
        +"                     Indicates the algorithm(s) part of the application-algorithm pair(s) for\n"
        +"                     which the presence of a random ID should be changed.\n"
        +"                     Value should be either the name of the algorithm or -all\n"
        +"                     If the value is -all, every application indicated by the --app argument will\n"
        +"                     be paired with every algorithm registered in the namespace system's list\n"
        +"                     of all applications.\n"
        +"                     Note that, while you do not need it to be registered to operate on an\n"
        +"                     individual algorithm, it will need to be registered to be brought up\n"
        +"                     using -all.\n"
        +"                *--default=<value>\n"
        +"                     When adding a random ID, this is the value to be used as the random ID for all\n"
        +"                     already existing experiments that are affected.\n"
        +"                     When removing a random ID, experiments in the affected paths that have this\n"
        +"                     random ID will be kept, all others will be discarded.\n"
        +"                *(optional) --fixed=<value>\n"
        +"                     This is used to ensure that random ID usage will be the same for every\n"
        +"                     application-algorithm pair indicated by the arguments. Pairs that already\n"
        +"                     match the desired setting will be skipped.\n"
        +"                     If this argument is left off, every indicated pair will change whether\n"
        +"                     or not it is using a random ID.\n"
        +"                     Valid values are true to use a random ID or false to not use a random ID.\n"
        +"        (3) joint-break\n"
        +"                Either adds or removes the file path break that will follow after the timestamp\n"
        +"                and/or the random ID of the experiments that fall under the application-algorithm\n"
        +"                pair(s) indicated by the arguments.\n"
        +"            Relevant arguments:\n"
        +"                *--app=<value>\n"
        +"                     Indicates the application(s) part of the application-algorithm pair(s) for\n"
        +"                     which the presence of a break after the timestamp/random ID should be changed.\n"
        +"                     Value should be either the name of the application or -all\n"
        +"                     If the value is -all, every algorithm indicated by the --alg argument will\n"
        +"                     be paired with every application registered in the namespace system's list\n"
        +"                     of all applications.\n"
        +"                     Note that, while you do not need it to be registered to operate on an\n"
        +"                     individual application, it will need to be registered to be brought up\n"
        +"                     using -all.\n"
        +"                *--alg=<value>\n"
        +"                     Indicates the algorithm(s) part of the application-algorithm pair(s) for\n"
        +"                     which the presence of a break after the timestamp/random ID should be changed.\n"
        +"                     Value should be either the name of the algorithm or -all\n"
        +"                     If the value is -all, every application indicated by the --app argument will\n"
        +"                     be paired with every algorithm registered in the namespace system's list\n"
        +"                     of all applications.\n"
        +"                     Note that, while you do not need it to be registered to operate on an\n"
        +"                     individual algorithm, it will need to be registered to be brought up\n"
        +"                     using -all.\n"
        +"                *(optional) --fixed=<value>\n"
        +"                     This is used to ensure that the use of a break after a timestamp/random ID\n"
        +"                     will be the same for every application-algorithm pair indicated by the\n"
        +"                     arguments. Pairs that already match the desired setting will be skipped.\n"
        +"                     If this argument is left off, every indicated pair will change whether\n"
        +"                     or not it is using a timestamp.\n"
        +"                     Valid values are true to use a path break or false to not use a path break.\n"
        +"        (4) swap\n"
        +"                For the indicated application or algorithm, changes the position in the file path\n"
        +"                of the two parameters indicated by the given arguments.\n"
        +"                Note that file path breaks are tied to the parameter and not the position.\n"
        +"                The use or otherwise of path breaks will be swapped along with the parameters.\n"
        +"            Relevant arguments:\n"
        +"                *ONE OF:\n"
        +"                     --app=<value>\n"
        +"                         Indicates that the parameter swap is being performed on the given application\n"
        +"                         Value should be the name of the application.\n"
        +"                     --alg=<value>\n"
        +"                         Indicates that the parameter swap is being performed on the given algorithm\n"
        +"                         Value should be the name of the algorithm.\n"
        +"                *<value>(x2)\n"
        +"                     The parameters to be swapped.\n"
        +"                     Value should either be the name of the parameter or its numerical index in the\n"
        +"                     current ordering. (The application/algorithm specifier is index 0, so the very\n"
        +"                     first parameter index is 1.)\n"
        +"        (5) break\n"
        +"                Changes whether or not there is a file path break following the indicated parameter\n"
        +"                in the indicated application or algorithm.\n"
        +"                Note that if there is a timestamp or a random ID in use, then there will always be\n"
        +"                a file break following the final parameter of either the application or algorithm\n"
        +"                (whichever is last), regardless of what the file path break variable is set to for\n"
        +"                that parameter.\n"
        +"            Relevant arguments:\n"
        +"                *ONE OF:\n"
        +"                     --app=<value>\n"
        +"                         Indicates that the path break change is being performed on the given application\n"
        +"                         Value should be the name of the application.\n"
        +"                     --alg=<value>\n"
        +"                         Indicates that the path break change is being performed on the given algorithm\n"
        +"                         Value should be the name of the algorithm.\n"
        +"                *--at=<value>\n"
        +"                     The parameter/position for which to change whether or not there is a file bath break\n"
        +"                     following it.\n"
        +"                     Value should either be the name of the parameter to put/remove a break after or the\n"
        +"                     numerical index of the part. For application/algorithm specifier (index 0) you can\n"
        +"                     alternatively use the special value <START>.\n"
        +"                *(optional) --fixed=<value>\n"
        +"                     This is used to ensure that the a break either is or isn't used after the given\n"
        +"                     parameter/position, rather than just changing the value. If the use of a break\n"
        +"                     already takes on this value, nothing happens.\n"
        +"                     Valid values are true to use a path break or false to not use a path break.\n"
        +"        (6) add\n"
        +"                Inserts the given parameter into the given application/algorithm at/directly in front\n"
        +"                of the given position/parameter. Existing experiments will be assigned the given default\n"
        +"                value to use in the spot for the parameter in their file paths.\n"
        +"            Relevant arguments:\n"
        +"                *ONE OF:\n"
        +"                     --app=<value>\n"
        +"                         Indicates that the parameter should be added to the given application\n"
        +"                         Value should be the name of the application.\n"
        +"                     --alg=<value>\n"
        +"                         Indicates that the parameter should be added to the given algorithm\n"
        +"                         Value should be the name of the algorithm.\n"
        +"                *--at=<value>\n"
        +"                     The parameter/position at/in front of which the given parameter should be inserted\n"
        +"                     Value should either be the name of the parameter in front of which the given parameter\n"
        +"                     should be inserted or the numerical index at which the parameter should be inserted\n"
        +"                     If it is being added to the end, either the numerical index or the special value\n"
        +"                     <END> can be used.\n"
        +"                *<value>\n"
        +"                     The name of the parameter to add to the path. An error will occur if this parameter\n"
        +"                     does not exist in the parameter file for the specified application/algorithm.\n"
        +"                *--default=<value>\n"
        +"                     This is the value to be used as the as the value of the parameter in the file path for\n"
        +"                     all already existing experiments that are affected.\n"
        +"                *(optional) --sep=<value>\n"
        +"                     This is used to indicate whether or not a file path separator should follow the\n"
        +"                     inserted parameter. If left out, the default will be false.\n"
        +"                     Valid values are true to use a path break or false to not use a path break.\n"
        +"        (7) remove\n"
        +"                Removes the given parameter (or the parameter at the given position) from the file paths\n"
        +"                of experiments performed with the given applications/algorithms. Any experiments where\n"
        +"                the parameter value matches the given default will be kept, all others will be discarded.\n"
        +"            Relevant arguments:\n"
        +"                *ONE OF:\n"
        +"                     --app=<value>\n"
        +"                         Indicates that the parameter should be removed from the given application\n"
        +"                         Value should be the name of the application.\n"
        +"                     --alg=<value>\n"
        +"                         Indicates that the parameter should be removed from the given algorithm\n"
        +"                         Value should be the name of the algorithm.\n"
        +"                *<value>"
        +"                     The parameter/position to remove from the file path.\n"
        +"                     Value should either be the name of the parameter to remove or the numerical index\n"
        +"                     of the part.\n"
        +"                *--default=<value>\n"
        +"                     Experiments in the affected paths where the indicated parameter that have this\n"
        +"                     value will be kept, all others will be discarded.\n"
        +"        (8) info\n"
        +"                Prints information on the pathing setup for the indicated applications, algorithms, or\n"
        +"                application-algorithm pairs.\n"
        +"                If printing information on individual applications or algorithms, each entry will begin\n"
        +"                with a line formateed: application/algorithm_name:\n"
        +"                and be followed with a version of what the file path for that application/algorithm is\n"
        +"                formatted like with three key differences.\n"
        +"                   1) There are spaces between each of the parameter names and separator symbols.\n"
        +"                   2) Instead of the usual app/alg name indicator at the start (e.g. app-im for\n"
        +"                      application im), the symbol <START> is used.\n"
        +"                   3) After the final separator symbol, the symbol <END> is used.\n"
        +"               If printing information on application-algorithm pairs, each entry will begin with a line\n"
        +"               formatted: application_name   -   algorithm_name:\n"
        +"               and be followed with one of the following (The value of 'sep' will be _ if the pair does\n"
        +"               not have a path separator following their timestamp/random ID and / if it does.):\n"
        +"                   1) (If the pair uses neither a timestamp nor a random ID) Nothing sep\n"
        +"                   2) (If the pair uses only a timestamp) Timestamp sep\n"
        +"                   3) (If the pair uses only a random ID) Random ID sep\n"
        +"                   4) (If the pair uses both a timestamp and a random ID) Timestamp _ Random ID sep\n"
        +"            Relevant arguments:\n"
        +"                *AT LEAST ONE OF:\n"
        +"                     --app=<value>\n"
        +"                         If the --alg argument is also provided, this indicates the application part(s)\n"
        +"                         of the application-algorithm pairs to display information on.\n"
        +"                         Otherwise, this indicates the application(s) to display information on.\n"
        +"                         Value should be the name of the application or -all. If the value is -all and\n"
        +"                         the --alg argument is also provided, then the algorithm(s) indicated by the\n"
        +"                         --alg argument will be paired with every application registered in the namespace\n"
        +"                         system and information on each pair will be printed.\n"
        +"                         If the value is -all and the --alg argument is not provided, then information\n"
        +"                         on every application registered in the namespace system will be printed.\n"
        +"                     --alg=<value>\n"
        +"                         If the --app argument is also provided, this indicates the algorithm part(s)\n"
        +"                         of the application-algorithm pairs to display information on.\n"
        +"                         Otherwise, this indicates the algorithms(s) to display information on.\n"
        +"                         Value should be the name of the algorithm or -all. If the value is -all and\n"
        +"                         the --app argument is also provided, then the application(s) indicated by the\n"
        +"                         --app argument will be paired with every algorithm registered in the namespace\n"
        +"                         system and information on each pair will be printed.\n"
        +"                         If the value is -all and the --app argument is not provided, then information\n"
        +"                         on every algorithm registered in the namespace system will be printed.\n"
        +"        (9) list\n"
        +"                Lists all applications, algorithms, or both that have been registered with the\n"
        +"                namspace system.\n"
        +"            Relevant arguments:\n"
        +"                *<value>\n"
        +"                     Indicates whether you want a list of registered applications, algorithms, or both.\n"
        +"                     Valid values are app or 1 for a list of registered applications, alg or 2 for a\n"
        +"                     list of registered algorithms, or both or 3 for both.\n"
        +"        (10) register\n"
        +"                Adds the given application/algorithm to the namespace system's list of all\n"
        +"                applications and algorithms.\n"
        +"            Relevant arguments:\n"
        +"                *ONE OF:\n"
        +"                     --app=<value>\n"
        +"                         Indicates that the given value should be registered as an application.\n"
        +"                         Value should be the name of the application.\n"
        +"                     --alg=<value>\n"
        +"                         Indicates that the given value should be registered as an algorithm.\n"
        +"                         Value should be the name of the algorithm.\n"
        +"        (11) unregister\n"
        +"                 Removes the given application/algorithm from the namespace system's list of all\n"
        +"                 applications and algorithms.\n"
        +"            Relevant arguments:\n"
        +"                *ONE OF:\n"
        +"                     --app=<value>\n"
        +"                         Indicates that the given value should be removed from the list of registered\n"
        +"                         applications.\n"
        +"                         Value should be the name of the application.\n"
        +"                     --alg=<value>\n"
        +"                         Indicates that the given value should be removed from the list of registered\n"
        +"                         algorithms.\n"
        +"                         Value should be the name of the algorithm.\n"
        )
    print(usage)
        
    
    
if __name__ == "__main__":
    if len(sys.argv) <= 1:
        printUsage()
        exit(0)
        
    mode = getMode(sys.argv[1])
    if mode == -1:
        print("Invalid mode. Run without arguments to see usage details.")
        exit(0)
        
    try:
        if mode == 0:
            if len(sys.argv) > 3:
                print("Too many arguments. Run without arguments to see usage details.")
                exit(0)
            if len(sys.argv) == 2:
                namespace.invert()
            else:
                app = False
                arg = sys.argv[2]
                if arg in baseRightApp:
                    app = True
                elif arg in baseRightAlg:
                    app = False
                else:
                    print("Second argument not recognized. Run without arguments to see usage details.")
                    exit(0)
                namespace.invert(True, app)
        elif mode == 1:
            if len(sys.argv) < 5:
                print("Too few arguments. Timestamp mode expects, at minimum, an application, an algorithm," 
                     " and a default value. Run without arguments to see usage details.")
                exit(1)
            elif len(sys.argv) > 6:
                print("Too many arguments. Timestamp mode expects, an application, an algorithm," 
                     " a default value, and, optionally, a value that the timestamp property to be fixed to "
                     "(rather than just changing from current setting). Run without arguments to see usage details.")
                exit(1)
            else:
                specs = [fixedArg, algSpecifier, appSpecifier, defaultSpecifier]
                args = processArgs(sys.argv[2:], specs)
                if args[0] is None or args[1] is None or args[3] is None:
                    print("Timestamp mode expects, an application, an algorithm," 
                     " a default value, and, optionally, a value that the timestamp property to be fixed to "
                     "(rather than just changing from current setting). Run without arguments to see usage details.")
                    exit(1)
                elif args[2] is not None:
                    app = args[0]
                    alg = args[1]
                    defa = args[3]
                    namespace.toggleTimestamp(app, alg, defa)
                else:
                    app = args[0]
                    alg = args[1]
                    fix = args[2]
                    defa = args[3]
                    namespace.toggleTimestamp(app, alg, defa, fix)
        elif mode == 2:
            if len(sys.argv) < 5:
                print("Too few arguments. Random Id mode expects, at minimum, an application, an algorithm," 
                     " and a default value. Run without arguments to see usage details.")
                exit(1)
            elif len(sys.argv) > 6:
                print("Too many arguments. Random Id mode expects, an application, an algorithm," 
                     " a default value, and, optionally, a value that the timestamp property to be fixed to "
                     "(rather than just changing from current setting). Run without arguments to see usage details.")
                exit(1)
            else:
                specs = [fixedArg, algSpecifier, appSpecifier, defaultSpecifier]
                args = processArgs(sys.argv[2:], specs)
                if args[0] is None or args[1] is None or args[3] is None:
                    print("Timestamp mode expects, an application, an algorithm," 
                     " a default value, and, optionally, a value that the timestamp property to be fixed to "
                     "(rather than just changing from current setting). Run without arguments to see usage details.")
                    exit(1)
                elif args[2] is not None:
                    app = args[0]
                    alg = args[1]
                    defa = args[3]
                    namespace.toggleTimestamp(app, alg, defa)
                else:
                    app = args[0]
                    alg = args[1]
                    fix = args[2]
                    defa = args[3]
                    namespace.toggleTimestamp(app, alg, defa, fix)
        elif mode == 3:
            if len(sys.argv) < 4:
                print("Too few arguments. Setting the file path break after the timestamp/random id expects, at minimum, an application and an algorithm." 
                     " Run without arguments to see usage details.")
                exit(1)
            elif len(sys.argv) > 5:
                print("Too many arguments. Setting the file path break after the timestamp/random id mode expects, an application, an algorithm," 
                     " and, optionally, a value(true or false) that the timestamp property to be fixed to "
                     "(rather than just changing from current setting). Run without arguments to see usage details.")
                exit(1)
            else:
                specs = [fixedArg, algSpecifier, appSpecifier]
                args = processArgs(sys.argv[2:], specs)
                if args[0] is None or args[1] is None or args[3] is None:
                    print("Setting the file path break after the timestamp/random id mode expects, an application, an algorithm," 
                     " and, optionally, a value(true or false) that the path break property to be fixed to "
                     "(rather than just changing from current setting). Run without arguments to see usage details.")
                    exit(1)
                elif args[2] is not None:
                    app = args[0]
                    alg = args[1]
                    defa = args[3]
                    namespace.toggleTimestamp(app, alg, defa)
                else:
                    app = args[0]
                    alg = args[1]
                    fix = args[2]
                    defa = args[3]
                    namespace.toggleTimestamp(app, alg, defa, fix)
        elif mode == 4:
            if len(sys.argv) != 5:
                print("Incorrect number of arguments. Swapping requires one of either"
                      " an application or an algorithm to perform the swap on "
                      "and the pair of parameters to swap. "
                      "Run without arguments to see usage details.")
                exit(1)
            else:
                specs = [algSpecifier, appSpecifier, basicSpecifier]
                args = processArgs(sys.argv[2:], specs, 2)
                if args[4] is None or args[5] is None:
                    print("Swapping requires one of either"
                      " an application or an algorithm to perform the swap on "
                      "and the pair of parameters to swap. "
                      "Run without arguments to see usage details.")
                    exit(1)
                elif args[0] is None:
                    namespace.swap(algorithms_index, args[1], args[4], args[5])
                else:
                    namespace.swap(applications_index, args[0], args[4], args[5])
        elif mode == 5:
            if len(sys.argv) < 4:
                print("Setting a file path break expects,"
                      "one of either an application or an algorithm, "
                      "a parameter/position to set the break for,"
                      " and, optionally, a value(true or false) that the path break property to be fixed to "
                     "(rather than just changing from current setting)."
                     " Run without arguments to see usage details.")
                exit(1)
            elif len(sys.argv) > 5:
                print("Setting a file path break expects,"
                      "one of either an application or an algorithm, "
                      "a parameter/position to set the break for,"
                      " and, optionally, a value(true or false) that the path break property to be fixed to "
                     "(rather than just changing from current setting)."
                     " Run without arguments to see usage details.")
                exit(1)
            else:
                specs = [fixedArg, algSpecifier, appSpecifier, atSpecifier]
                args = processArgs(sys.argv[2:], specs)
                if (((args[0] is None and args[1] is None) or (args[0] is not None and args[1] is not None))
                    or args[6] is None):
                    print("Setting a file path break expects,"
                      "one of either an application or an algorithm, "
                      "a parameter/position to set the break for,"
                      " and, optionally, a value(true or false) that the path break property to be fixed to "
                     "(rather than just changing from current setting)."
                     " Run without arguments to see usage details.")
                    exit(1)
                else:
                    index = None
                    ident = None
                    if args[0] is not None:
                        index = applications_index
                        ident = args[0]
                    else:
                        index = algorithms_index
                        ident = args[1]
                        
                    if args[2] is not None:
                        namespace.toggleBreak(index, ident, args[6], True, args[2])
                    else:
                        namespace.toggleBreak(index, ident, args[6])
        elif mode == 6:
            #Insert: at(6), default(3), app/alg(0/1), basic(4), sep(8)
            if len(sys.argv) < 6 or len(sys.argv) > 7:
                print("Inserting a parameter into the path requires either an application or"
                      " an algorithm to insert it into, the location in front of "
                      "which the parameter should be inserted, the default value that"
                      " should be used for this parameter for all currently existing experiment"
                      " results, the name of the parameter to insert, and, optionally, "
                      "whether the new parameter should be followed by a path separator (default is false)."
                      " Run without arguments to see usage details.")
                exit(1)
            else:
                specs = [algSpecifier, appSpecifier, atSpecifier, defaultSpecifier, 
                         sepSpecifier, basicSpecifier]
                args = processArgs(sys.argv[2:], specs, 1)
                if (args[0] is not None and args[1] is not None 
                    or len(sys.argv) == 6 and args[8] is not None):
                    print("Inserting a parameter into the path requires either an application or"
                      " an algorithm to insert it into, the location in front of "
                      "which the parameter should be inserted, the default value that"
                      " should be used for this parameter for all currently existing experiment"
                      " results, the name of the parameter to insert, and, optionally, "
                      "whether the new parameter should be followed by a path separator (default is false)."
                      " Run without arguments to see usage details.")
                    exit(1)
                useSep = False
                if args[8] is not None:
                    useSep = args[8]
                    
                if args[0] is not None:
                    namespace.addParam(applications_index, args[0], args[4], useSep, args[6], args[3])
                else:
                    namespace.addParam(algorithms_index, args[1], args[4], useSep, args[6], args[3])
        elif mode == 7:
            #Remove: basic(4), default(3), app/alg(0/1)
            if len(sys.argv) != 5:
                print("Removing a parameter from the path requires either an application or"
                      " an algorithm to remove it from, the name of the parameter to remove"
                      ", and the default value (experiment results where the parameter took on"
                      " this value will be kept, all others will be discarded)."
                      " Run without arguments to see usage details.")
                exit(1)
            else:
                specs = [appSpecifier, algSpecifier, defaultSpecifier, basicSpecifier]
                args = processArgs(sys.argv[2:], specs, 1)
                if args[0] is not None and args[1] is not None:
                    print("Removing a parameter from the path requires either an application or"
                      " an algorithm to remove it from, the name of the parameter to remove"
                      ", and the default value (experiment results where the parameter took on"
                      " this value will be kept, all others will be discarded)."
                      " Run without arguments to see usage details.")
                    exit(1)
                if args[0] is not None:
                    namespace.removeParam(applications_index, args[0], args[4], args[3])
                else:
                    namespace.removeParam(algorithms_index, args[1], args[4], args[3])
        elif mode == 8:
            #Info: app(0) and/or alg(1)
            if len(sys.argv) < 3 or len(sys.argv) > 4:
                print("The info mode requires either the application to list the "
                      "pathing information for, the algorithm to list the information for, "
                      "or the application and algorithm pair to list the joint pathing information."
                      " Run without arguments to see usage details.")
                exit(1)
            specs = [appSpecifier, algSpecifier]
            args = processArgs(sys.argv[2:],specs)
            namespace.printList(args[0], args[1])
        elif mode == 9:
            #List: mode2(7)
            if len(sys.argv) != 3:
                print("The list mode requires an argument listing whether it "
                      "should list all applications (app), algorithms (alg), or both (both)."
                      " Run without arguments to see usage details.")
                exit(1)
            specs = [mode2Specifier]
            args = processArgs(sys.argv[2:],specs)
            val = args[7]
            data = namespace.listAll()
            if val == applications_index or val == joint_index:
                print("Applications:")
                for a in data["applications"]:
                    print("    " + a)
                    
            if val == joint_index:
                print()
                
            if val == algorithms_index or val == joint_index:
                print("Algorithms:")
                for a in data["algorithms"]:
                    print("    " + a)
            
            print()
        elif mode == 10:
            #Register: app/alg(0/1)
            if len(sys.argv) != 3:
                print("Registering an application or algorithm requires "
                      "providing the application or algorithm to be registered."
                      " Run without arguments to see usage details.")
                exit(1)
            specs = [appSpecifier, algSpecifier]
            args = processArgs(sys.argv[2:],specs)
            if args[0] is not None:
                namespace.register(applications_index, args[0])
            else:
                namespace.register(algorithms_index, args[1])
        elif mode == 11:
            #De-register: app/alg(0/1)
            if len(sys.argv) != 3:
                print("Unregistering an application or algorithm requires "
                      "providing the application or algorithm to be unregistered."
                      " Run without arguments to see usage details.")
                exit(1)
            specs = [appSpecifier, algSpecifier]
            args = processArgs(sys.argv[2:],specs)
            if args[0] is not None:
                namespace.deregister(applications_index, args[0])
            else:
                namespace.deregister(algorithms_index, args[1])
        print("Complete")
    except Exception as e:
        print(str(e))
        exit(1)

    