#!/bin/python
from dotenv import load_dotenv

load_dotenv()

import os
import importlib
import sys
import glob
from langchain.globals import set_verbose, set_debug

def import_module(module_name, verbose=False):
    try:
        imported_module = importlib.import_module(module_name)
        if verbose:
            print(f"Imported {imported_module}")
        return imported_module
    except ImportError:
        if verbose:
            print(f"Module {module_name} not found.")
        return None

def import_directory(directory, verbose=False, prefix=""):    
    imported_modules = {}

    init_file = os.path.join(directory, '__init__.py')
    if os.path.isfile(init_file):
        module_name = directory.replace('/', '.')
        imported_modules[module_name] = import_module(module_name, verbose)

    for filename in glob.glob(os.path.join(directory, '*.py')):
        if not filename.endswith('__init__.py'):
            module_name = filename[:-3].replace('/', '.')
            imported_modules[module_name] = import_module(module_name, verbose)
            
    for subdirectory in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, subdirectory)):
            imported_modules.update(import_directory(os.path.join(directory, subdirectory), verbose))

    return imported_modules

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()

if args.verbose:
    verbose = True
else:
    verbose = False

def import_all():
    # LIBS = [name for name in os.listdir('lib') if os.path.isdir(os.path.join('lib', name))]

    DIRECTORIES = [
        "lib",
        "app"
    ]
    
    for directory in DIRECTORIES:
        globals().update(import_directory(directory, verbose))
    
import_all()

def reload_module(module_name, verbose=False):
    try:
        if verbose:
            print(f"Reloading {module_name}")
        return importlib.reload(sys.modules[module_name])
    except KeyError:
        print(f"Error: Module {module_name} not found.")

def reload(verbose: bool = verbose):
    for module in list(sys.modules.keys()):
        if module.startswith('app'):
            reload_module(module, verbose)

from lib.chamber_py import Chamber
Chamber.load()