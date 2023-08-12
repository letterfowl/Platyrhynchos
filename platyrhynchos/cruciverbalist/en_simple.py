from tqdm_loggable.auto import tqdm

from ..commons.exceptions import DatabaseException
from ..commons.logger import logger
from ..commons.settings import settings
from ..commons.utils import random
from ..crossword.colrow import ColRow
from ..exclusive import download_db
from .exclusive_word_base import ExclusiveWordBaseCruciverbalist
from .old_base import CruciverbalistOldBase

class EnglishSimpleCruciverbalist(ExclusiveWordBaseCruciverbalist, CruciverbalistOldBase):
    @property
    def DB_FILE(self) -> str:
        return "en_simple.db"

    def eval_colrow(self, colrow: ColRow) -> float:
        """
        Evaluates the ColRow as the next one to add a word to.
        Returns the inverse of the number of words colliding with the colrow.
        """
        return 1 / (len(list(colrow.cross_words())) + 1)

    def eval_word(self, word: str, colrow: ColRow) -> int:
        """Evaluate the word as an insertion into a ColRow."""
        return len(word) + len(list(colrow.cross_words()))
