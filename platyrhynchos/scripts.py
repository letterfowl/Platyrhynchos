"""Implements simple scripts as functions"""
import asyncio
from contextlib import suppress
from os import remove as remove_file

from .commons.utils import app_dir
from .crossword.improvable import CrosswordImprovable

from time import perf_counter

class catchtime:
    def __enter__(self):
        self.time = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.time = perf_counter() - self.time
        self.readout = f'Time: {self.time:.3f} seconds'
        print(self.readout)


def print_qualities(crossword: CrosswordImprovable):
    """Prints the most important information about the crossword"""
    crossword.print_rich_grid()
    print("\n", "Words:", *list(crossword.words.keys()), sep="\n")
    print()
    print("Density:", len(crossword.letters) / crossword.size)
    print("Words:", len(crossword.words))
    print("Crossings:", len(crossword.crossings))
    print("Crossings per word:", len(crossword.crossings) / len(crossword.words))
    print("Crossings per letter:", len(crossword.crossings) / len(crossword.letters))
    print("Crossings per field:", len(crossword.crossings) / crossword.size)


def en_simple_prep():
    from .cruciverbalist.en_simple import EnglishSimpleCruciverbalist

    with suppress(FileNotFoundError):
        remove_file(app_dir("user_cache_dir", "en_simple.db"))
    EnglishSimpleCruciverbalist()


async def direct_run_routine():
    from asyncio import run

    from .director.direct_search import generate_crossword

    with catchtime():
        crossword = await generate_crossword(10, 10, 12)
    print_qualities(crossword)
    


def direct_run():
    asyncio.run(direct_run_routine())
    
async def annealing_run_routine():
    from asyncio import run

    from .director.simulated_annealing import generate_crossword

    with catchtime():
        crossword = await generate_crossword(10, 10, 30)
    print_qualities(crossword)

def annealing_run():
    asyncio.run(annealing_run_routine())