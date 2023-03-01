import doctest
import os
import sys

sys.path.insert(0, os.getcwd())
DOCTEST_PATH = "doctests"

for i in os.listdir(DOCTEST_PATH):
    if i.endswith(".md"):
        doctest.testfile(os.path.join(DOCTEST_PATH, i), verbose=True, report=True)