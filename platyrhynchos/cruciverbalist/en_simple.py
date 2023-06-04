from tempfile import NamedTemporaryFile, _TemporaryFileWrapper

from tqdm_loggable.auto import tqdm

from ..commons.alphabit import Alphabit
from ..commons.exceptions import DatabaseException
from ..commons.utils import random
from ..commons.settings import settings
from ..crossword.colrow import ColRow
from ..exclusive import download_db, get_random, get_regex, get_regex_w_alphabit
from .base import CruciverbalistBase


class EnglishSimpleCruciverbalist(CruciverbalistBase):
    DB_FILE = settings.en_simple.db_file
    RUN_WITH_ALPHABIT = settings.en_simple["use_alphabit"]

    def __init__(self) -> None:
        """Prepares the database"""
        download_db(self.DB_FILE)
        super().__init__()

    def eval_colrow(self, colrow: ColRow) -> float:
        """
        Evaluates the ColRow as the next one to add a word to.
        Returns the number of words colliding with the colrow with random noise.
        """
        return -len(list(colrow.cross_words()))*random.random()

    def select_by_regex(self, regexes: list[str], previous: list[str]|None = None) -> list[str] | None:
        """
        Select compatible words using regex. It accepts a list of regular expressions and checks all one by one.
        """
        for i in [i.upper() for i in regexes]:
            if self.RUN_WITH_ALPHABIT:
                # Returns an alphabit query
                alp = Alphabit(i).to_query()
                if ret := get_regex_w_alphabit(regex=i, alphabit=alp, previous=previous):
                    return ret
            elif ret := get_regex(regex=i, previous=previous):
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
