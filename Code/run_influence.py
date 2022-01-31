# -*- coding: utf-8 -*-

from importlib import import_module
import sys

def run(name,package):
    module = import_module(name,package)
    module.main()
    
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("expecting a package name and a file name to run\n")
    else:
        name = "." + sys.argv[2]
        package = sys.argv[1]
        run(name, package)