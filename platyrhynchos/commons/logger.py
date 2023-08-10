"""
Implements logging using the loguru library. It also intercepts all other loggers and writes their output to out.log
"""
import logging
import sys

from loguru import logger

from .settings import settings
from .utils import app_dir

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
logger.add(app_dir('user_log_path')+"/log.log", retention="1 day")