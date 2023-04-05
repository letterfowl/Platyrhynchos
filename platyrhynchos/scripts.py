from os import remove as remove_file
from .commons.utils import app_dir
from contextlib import suppress
from .cruciverbalists.en_simple import prepare_database

def en_simple_prep():
    with suppress(FileNotFoundError):
        remove_file(app_dir("user_cache_dir", "en_simple.db"))
    prepare_database()
