"""
This library contains all functions and classes that do not implement the logic of the program.
Rather they are technical tools
"""
from os import makedirs
from os.path import join as join_path
from random import Random
from typing import Literal

from platformdirs import PlatformDirs as _PlatformDirs

DEBUG = True

_APP_DIRS = _PlatformDirs(appname="platyrhynchos")


def app_dir(
    name: Literal[
        "user_data_dir",
        "user_config_dir",
        "user_cache_dir",
        "user_state_dir",
        "user_log_dir",
        "user_documents_dir",
        "user_runtime_dir",
        "site_data_dir",
        "site_config_dir",
        "site_cache_dir",
        "user_data_path",
        "user_config_path",
        "user_cache_path",
        "user_state_path",
        "user_log_path",
        "user_documents_path",
        "user_runtime_path",
        "site_data_path",
        "site_config_path",
        "site_cache_path",
    ],
    file_name: str = "",
):
    path = f"./tmp/{name}/" if DEBUG else getattr(_APP_DIRS, name)
    if isinstance(path, str):
        makedirs(path, exist_ok=True)
    return join_path(path, file_name)


random = Random("jebać falubaz")
