#!/usr/bin/env python
import os
import sys

cwd = os.path.dirname(os.path.realpath(sys.argv[0]))
dir_local = os.path.join(cwd, 'carbon')
#os.system(f"python {dir_local}/resources/NBTest/ConvertNBTest.py")
os.system(f"pytest {dir_local}/tests")
print(f"ran tests from local directory {dir_local}")
