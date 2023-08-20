"""Implements simple scripts as functions"""
import asyncio
from contextlib import suppress
from os import remove as remove_file
from time import perf_counter

from .commons.utils import app_dir
from .crossword.improvable import CrosswordImprovable

WIDTH = 15
LENGTH = 10
WORDS = 40


class catchtime:
    def __enter__(self):
        self.time = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.time = perf_counter() - self.time
        self.readout = f"Time: {self.time:.3f} seconds"
        print(self.readout)


def print_qualities(crossword: CrosswordImprovable):
    """Prints the most important information about the crossword"""
    crossword.print_rich_grid()
    print("\n", "Words:", *list(crossword.words.keys()), sep="\n")
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
    from .director.direct_search import generate_crossword

    with catchtime():
        crossword = await generate_crossword(WIDTH, LENGTH, WORDS)
    print_qualities(crossword)


def direct_run():
    asyncio.run(direct_run_routine())


async def local_search_routine():
    from .director.local_search import generate_crossword

    with catchtime():
        crossword = await generate_crossword(WIDTH, LENGTH, WORDS)
    print_qualities(crossword)


def local_search_run():
    asyncio.run(local_search_routine())


async def simulated_annealing_routine():
    from .director.simulated_annealing import SimulatedAnnealingCrosswordSearch

    with catchtime():
        crossword_generator = SimulatedAnnealingCrosswordSearch(
            lambda x: len(x.crossings) / len(x.letters) > 0.35 and len(x.letters) / x.size > 0.8
        )
        crossword = await crossword_generator.run(WIDTH, LENGTH)
    print_qualities(crossword)
    return await crossword_generator.get_react_readable(crossword)


def simulated_annealing_run():
    asyncio.run(simulated_annealing_routine())
