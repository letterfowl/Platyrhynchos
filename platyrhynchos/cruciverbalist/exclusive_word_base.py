from abc import abstractmethod, ABC
from typing import Iterable
from ..exclusive import download_db, get_random, get_regex, get_regex_w_alphabit
from ..commons.alphabit import Alphabit
from ..commons.settings import settings
from ..commons.logger import logger
from ..commons.exceptions import DatabaseException

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
        self, regexes: Iterable[str], previous: Iterable[str] | None = None
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
                if ret := await get_regex_w_alphabit(i, alp.to_query(), list(previous)):
                    return ret
            elif ret := await get_regex(i, list(previous)):
                return ret
        return []

    async def start_word(self, max_size: int) -> str:
        """
        Get a random word from the database. This is useful for starting the crossword.
        """
        found_words = await get_random(max_size)
        # If there are any words in the database raise a DatabaseException.
        if found_words is None:
            raise DatabaseException("Couldn't find any words.")
        return found_words[0]