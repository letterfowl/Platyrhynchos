from tempfile import NamedTemporaryFile, _TemporaryFileWrapper

from tqdm_loggable.auto import tqdm

from ..commons.alphabit import Alphabit
from ..commons.exceptions import DatabaseException
from ..commons.logger import logger
from ..crossword.colrow import ColRow
from ..exclusive import download_db, get_random, get_regex, get_regex_w_alphabit
from .base import Cruciverbalist

URL = "https://cryptics.georgeho.org/data/clues.csv?_stream=on&_size=max"
RUN_WITH_ALPHABIT = True


class EnglishSimpleCruciverbalist(Cruciverbalist):
    def __init__(self) -> None:
        """Prepares the database"""
        download_db(URL)
        super().__init__()

    def _sql_regex(self, **kwargs):
        """
        Queries the database for regex. Uses get_regex_w_alphabit or get_regex query.
        Keyword arguments are parsed to the query for string interpolation.
        """
        if RUN_WITH_ALPHABIT:
            found = get_regex_w_alphabit(**kwargs)
        else:
            found = get_regex(**kwargs)
        return found if (found := [j[0] for j in found.fetchall()]) else None

    def eval_colrow(self, colrow: ColRow) -> int:
        """
        Evaluates the ColRow as the next one to add a word to.
        Returns the number of words colliding with the colrow.
        """
        return -len(list(colrow.cross_words()))

    def select_by_regex(self, regexes: list[str]) -> list[str] | None:
        """
        Select compatible words using regex. It accepts a list of regular expressions and checks all one by one.
        """
        for i in [i.upper() for i in regexes]:
            if RUN_WITH_ALPHABIT:
                # Returns an alphabit query
                alp = Alphabit(i).to_query()
                if ret := self._sql_regex(regex=i, alphabit=alp):
                    return ret
            elif ret := self._sql_regex(regex=i):
                return ret
        return None

    def eval_word(self, word: str, colrow: ColRow) -> int:
        """Evaluate the word as an insertion into a ColRow."""
        return len(word) + len(list(colrow.cross_words()))

    def start_word(self) -> str:
        """Get a random word from the database. This is useful for testing the crossword."""
        found_words = get_random()
        # If there are any words in the database raise a DatabaseException.
        if found_words is None:
            raise DatabaseException("Couldn't find any words.")
        return found_words[0]
