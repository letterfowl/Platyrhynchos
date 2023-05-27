from sys import platform

from ..commons.logger import logger

if platform == "emscripten":
    logger.info("Using pyodide")
    from .pyodide import *
else:
    logger.info("Using cpython")
    from .cpython import *
