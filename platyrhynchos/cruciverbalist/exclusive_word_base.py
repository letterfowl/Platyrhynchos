from abc import ABC, abstractmethod
import asyncio
from typing import AsyncGenerator, Iterable, Iterator

from ..commons.alphabit import Alphabit
from ..commons.exceptions import DatabaseException
from ..commons.logger import logger
from ..commons.settings import settings
from ..exclusive import (
    download_db,
    find_clues,
    get_random,
    get_regex,
    get_regex_w_alphabit,
)


class ExclusiveWordBaseCruciverbalist(ABC):
    """An abstract Cruciverbalist that uses the database imported from the exclusive module."""

    def __init__(self) -> None:
        """Prepares the database"""
        download_db(self.DB_FILE)
        super().__init__()

    @property
    @abstractmethod
    def DB_FILE(self) -> str:
        """The path to the database file."""

    RUN_WITH_ALPHABIT = settings.cruciverbalist["use_alphabit"]

    async def select_by_regex(
        self,
        regexes: Iterable[str],
        previous: list[str] | None = None,
        word_amount: int = 20,
    ) -> list[str]:
        """
        Select compatible words using regex. It accepts a list of regular expressions and checks all one by one.
        """
        previous = previous or []
        for i in [i.upper() for i in regexes]:
            if self.RUN_WITH_ALPHABIT:
                # Returns an alphabit query
                alp = Alphabit(i)
                logger.debug(
                    "Using alphabit: {}; which corresponds to {}",
                    alp.to_query(),
                    alp.as_letters(),
                )
                if ret := await get_regex_w_alphabit(
                    i, alp.to_query(), ",".join(previous), word_amount
                ):
                    return ret
            elif ret := await get_regex(i, ",".join(previous), word_amount):
                return ret
        return []

    async def iter_select_by_regex(
        self,
        regexes: Iterable,
        previous: list[str] | None = None,
        regex_per_query: int = 1,
        word_amount: int = 4,
    ) -> AsyncGenerator[list[str], None]:
        """
        Asynchronously iterates over a selection of words based on regular expressions.

        This method takes a list of regular expressions and iteratively selects words that match each regular expression. It yields a list of selected words for each iteration.

        Args:
            regexes (Iterable): A collection of regular expressions to match against.
            previous (list[str] | None, optional): A list of previously used words. Defaults to None.
            regex_per_query (int, optional): The number of regular expressions to process in each iteration. Defaults to 2.
            word_amount (int, optional): The desired number of selected words. Defaults to 10.

        Ret8rjs:
            AsyncGenerator[list[str], None]: An asynchronous generator that yields a list of words foun by a regex.
        """

        previous = previous or []
        regex_list = list(regexes)

        # Start first query ASAP
        old_task = self.select_by_regex(
            regex_list[:regex_per_query], previous, word_amount
        )

        # Prepare the rest of the queries
        slices = [
            regex_list[i : i + regex_per_query]
            for i in range(regex_per_query, len(regex_list), regex_per_query)
        ]
        word_promises = iter(
            self.select_by_regex(queries, previous, word_amount) for queries in slices
        )

        # Iterate over the next queries
        found = 0
        for new_task in word_promises:
            # Wait for the previous query to finish and yield the results
            words = await old_task
            yield words

            # Check if we have enough words
            found += len(words)
            if found >= word_amount:
                new_task.close()
                break

            old_task = new_task

    async def start_word(self, max_size: int) -> str:
        """
        Get a random word from the database. This is useful for starting the crossword.
        """
        found_words = await get_random(max_size)
        # If there are any words in the database raise a DatabaseException.
        if found_words is None:
            raise DatabaseException("Couldn't find any words.")
        return found_words[0]

    async def get_clues(self, words: list[str]) -> dict[str, str]:
        return {
            i[0]: i[-1] for i in await find_clues(",".join(f"'{k}'" for k in words))
        }
