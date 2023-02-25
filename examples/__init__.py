import doctest
import os
import sys

sys.path.insert(0, os.getcwd())

for i in os.listdir(os.path.dirname(__file__)):
    if i.endswith(".md"):
        doctest.testfile(i, report=True, raise_on_error=True)