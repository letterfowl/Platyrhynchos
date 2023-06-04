"""Implements simple scripts as functions"""
import asyncio
from contextlib import suppress
from os import remove as remove_file

from .commons.utils import app_dir


def en_simple_prep():
    from .cruciverbalist.en_simple import EnglishSimpleCruciverbalist
    with suppress(FileNotFoundError):
        remove_file(app_dir("user_cache_dir", "en_simple.db"))
    EnglishSimpleCruciverbalist()

async def direct_run_routine():
    from .director.direct_search import generate_crossword
    from asyncio import run
    crossword = await generate_crossword(10, 10, 12)
    print(crossword, "\n", "\n".join(crossword.words))
    
def direct_run():
    asyncio.run(direct_run_routine())