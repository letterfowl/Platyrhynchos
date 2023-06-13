from abc import ABC, abstractmethod
from typing import Iterable, Iterator

from ..commons.logger import logger
from ..commons.utils import random
from ..crossword.colrow import ColRow
from ..crossword.improvable import CrosswordImprovable


class CruciverbalistBase(ABC):
    # SAMPLE_SIZE = 100

    @abstractmethod
    def eval_colrow(self, colrow: ColRow) -> float:
        return

    def choose_colrows(self, crossword: CrosswordImprovable) -> Iterator[ColRow]:
        col_rows = crossword.iter_colrows()
        yield from sorted(col_rows, key=self.eval_colrow, reverse=True)

    @abstractmethod
    async def select_by_regex(self, regexes: list[str], previous: list[str]|None = None) -> list[str]:
        return

    @abstractmethod
    def eval_word(self, word: str, colrow: ColRow) -> int:
        return

    @abstractmethod
    async def start_word(self, max_size: int) -> str:
        return

    def _eval_word(self, word: str, colrow: ColRow) -> tuple[str, int]:
        return word, self.eval_word(word, colrow)

    async def find_words(self, colrow: ColRow) -> list[tuple[str, ColRow]]:
        words = await self.select_by_regex(list(colrow.yield_regexes()), colrow.crossword.words.keys())
        # if self.SAMPLE_SIZE is not None and self.SAMPLE_SIZE < len(words):
        #     words = random.sample(words, self.SAMPLE_SIZE)

        words_len = [self._eval_word(word, colrow) for word in words if word is not None]

        return_words = [
            (word, colrow) for word, _ in sorted(words_len, key=lambda x: x[1])
        ]
        logger.debug(f"Found {len(return_words)} words for {colrow}")
        return return_words

    async def find_word(self, colrows: ColRow | Iterable[ColRow]) -> tuple[str | None, ColRow | None]:
        if isinstance(colrows, ColRow):
            colrows = [colrows]
        for colrow in colrows:
            if words := await self.find_words(colrow):
                weights = [i+1 for i in range(len(words))]
                choice = random.choices(words, weights=weights, k=1)[0]
                logger.debug(f"Choice: {choice}")
                return choice
        return None, None
            

    async def choose_and_fill(self, crossword: CrosswordImprovable) -> tuple[str | None, ColRow | None]:
        colrows = self.choose_colrows(crossword)
        return await self.find_word(colrows)
