from sys import platform

from ..commons.logger import logger

if platform == "emscripten":
    logger.info("Using pyiodide")
    from .pyiodide import *
else:
    logger.info("Using cpython")
    from .cpython import *
