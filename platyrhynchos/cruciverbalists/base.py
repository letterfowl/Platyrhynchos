from abc import ABC, abstractmethod
from typing import Iterator, Iterable
from ..crossword.colrow import ColRow
from ..crossword.improvable import CrosswordImprovable

class Cruciverbalist(ABC):

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

    def find_words(self, colrows: Iterable[ColRow]) -> Iterator[tuple[str, ColRow]]:
        for colrow in colrows:
            words = self.select_by_regex(list(colrow.yield_regexes()))
            if words is None:
                continue
            words_sorted = sorted(words, key=lambda word: self.eval_word(word, colrow), reverse=True)
            yield from ((i, colrow) for i in words_sorted)

    def find_word(self, colrows: ColRow|Iterable[ColRow]) -> tuple[str|None, ColRow|None]:
        if isinstance(colrows, ColRow):
            colrows = [colrows]
        return next(self.find_words(colrows), (None, None))

    def choose_and_fill(self, crossword:CrosswordImprovable) -> tuple[str|None, ColRow|None]:
        colrows = self.choose_colrows(crossword)
        return self.find_word(colrows)
