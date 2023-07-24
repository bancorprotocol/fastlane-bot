"""
FLS - File Load Save (simple wrappers for loading and saving data)

:fsave:     save data into a file
:fload:     load data from a file
:join:      convenience wrapper for os.path.join

:VERSION HISTORY:

- v1.0: fload, fsave, join
- v1.0.1: minor change in output
- v1.1: json and yaml
- v1.2: copyright notice, license & canonic URL

:copyright:     (c) Copyright Stefan LOESCH / topaze.blue 2022; ALL RIGHTS RESERVED
:license:       [MIT](https://opensource.org/licenses/MIT)
:canonicurl:    https://github.com/topazeblue/TopazePublishing/blob/main/code/fls.py
"""
__VERSION__ = "1.2-noyaml"
__DATE__ = "06/Jan/2023"

import os as _os
import gzip as _gzip
import json as _json
#import yaml as _yaml

#########################################################
# FSAVE
def fsave(data, fn, path=None, binary=False, json=False, yaml=False, wrapper=None, quiet=True, compressed=False):
    """
    saves data to the file fn

    :data:          the data to be saved
    :fn:            the filename 
    :path:          the file path (default is "")
    :binary:        if True, the data is to be written as binary data*
    :json:          if True, the data is to be written as json data*
    :yaml:          if True, the data is to be written as yaml data*
    :wrapper:       a wrapper string where `{}` is replaced with the data
    :quiet:         if True, do not print info message
    :compressed:    use gz compression (implies binary*)

    *binary, json, yaml == True are mutually exclusive; behaviour is undefined otherwise
    """
    assert yaml is False
    if path is None:
        path = "."
    ffn = _os.path.join(path, fn)

    if not quiet: print (f"[fsave] Writing {fn} to {path}")
    
    if compressed: binary = True
    ftype = "wb" if binary else "w"

    if json:
        data = _json.dumps(data)
    
    if yaml:
        data = _yaml.safe_dump(data)

    if not wrapper is None:
        data = wrapper.format(data)
    
    if compressed:
        data = _gzip.compress(data.encode())

    with open (ffn, ftype) as f:
        f.write(data)

#########################################################
# FLOAD
def fload(fn, path=None, binary=False, json=False, yaml=False, wrapper=None, quiet=True, compressed=False):
    """
    loads data from the file fn

    :fn:            the filename 
    :path:          the file path (default is "")
    :binary:        if the data is to be written as binary data
    :json:          if True, the data is to be written as json data*
    :yaml:          if True, the data is to be written as yaml data*
    :wrapper:       a wrapper string where `{}` is replaced with the data
    :quiet:         if True, do not print info message
    :compressed:    use gz compression (implies binary)

    *binary, json, yaml == True are mutually exclusive; behaviour is undefined otherwise
    """
    assert yaml is False

    if path is None:
        path = "."
    ffn = _os.path.join(path, fn)

    if not quiet: print (f"[fload] Reading {fn} from {path}")

    if compressed: binary = True
    ftype = "rb" if binary else "r"
    with open (ffn, ftype) as f:
        data = f.read()
    
    if compressed:
        data = _gzip.decompress(data)

    if json:
        data = _json.loads(data)
    
    if yaml:
        data = _yaml.safe_load(data)

    if not wrapper is None:
        data = wrapper.format(data)
    return data

CSSWRAPPER = "\n<style>\n{}\n</style>\n"

#########################################################
# JOIN
def join(*args):
    "convenience wrapper for os.path.join"
    return _os.path.join(*args)