"""Implements simple scripts as functions"""
from contextlib import suppress
from os import remove as remove_file

from .commons.utils import app_dir


def en_simple_prep():
    from .cruciverbalist.en_simple import EnglishSimpleCruciverbalist
    with suppress(FileNotFoundError):
        remove_file(app_dir("user_cache_dir", "en_simple.db"))
    EnglishSimpleCruciverbalist()

def direct_run():
    from .director.direct_search import generate_crossword
    crossword = generate_crossword(10, 10, 12)
    print(crossword, "\n", "\n".join(crossword.words))