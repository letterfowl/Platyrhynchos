from sys import platform

if platform == "emscripten":
    from .pyiodide import *
else:
    from .cpython import *
