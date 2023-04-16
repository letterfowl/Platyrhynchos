from abc import ABC, abstractmethod
from typing import Iterable, Iterator

from ..commons.logger import logger
from ..commons.utils import random
from ..crossword.colrow import ColRow
from ..crossword.improvable import CrosswordImprovable


class Cruciverbalist(ABC):
    # SAMPLE_SIZE = 0.9
    SAMPLE_SIZE = 1

    @abstractmethod
    def eval_colrow(self, colrow: ColRow) -> int:
        return

    def choose_colrows(self, crossword: CrosswordImprovable) -> Iterator[ColRow]:
        col_rows = crossword.iter_colrows()
        yield from sorted(col_rows, key=self.eval_colrow, reverse=True)

    @abstractmethod
    def select_by_regex(self, regexes: list[str]) -> list[str]:
        return

    @abstractmethod
    def eval_word(self, word: str, colrow: ColRow) -> int:
        return

    @abstractmethod
    def start_word(self) -> str:
        return

    def _eval_word(self, word: str, colrow: ColRow) -> tuple[str, int]:
        return word, self.eval_word(word, colrow)

    def find_words(self, colrows: Iterable[ColRow]) -> Iterator[tuple[str, ColRow]]:
        for colrow in colrows:
            words = self.select_by_regex(list(colrow.yield_regexes()))
            if words is None:
                continue
            if self.SAMPLE_SIZE != 1:
                words_size = int(len(words) ** self.SAMPLE_SIZE)
                words = random.sample(words, words_size)

            words_len = set(map(self._eval_word, words, [colrow for _ in words]))

            while words_len:
                word, val = max(words_len, key=lambda x: x[1])
                words_len.remove((word, val))
                logger.debug("Found: {}", word)
                yield word, colrow

    def find_word(self, colrows: ColRow | Iterable[ColRow]) -> tuple[str | None, ColRow | None]:
        if isinstance(colrows, ColRow):
            colrows = [colrows]
        return next(self.find_words(colrows), (None, None))

    def choose_and_fill(self, crossword: CrosswordImprovable) -> tuple[str | None, ColRow | None]:
        colrows = self.choose_colrows(crossword)
        return self.find_word(colrows)
