"""Word wrapper over the ColRow and Crossword class"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..commons.exceptions import WordNotFoundError
from ..commons.misc import Coord
from ..crossword.improvable import CrosswordImprovable
from .base import Crossword
from .colrow import ColRow


@dataclass
class Word:
    crossword: Crossword
    colrow: ColRow
    word: str
    letter_fields: set[Coord]

    def _get_indexes_of_crossing_colrows(self) -> set[int]:
        return {i for _, i in self.letter_fields} if self.colrow.is_column else {i for i, _ in self.letter_fields}

    @classmethod
    def from_crossword(cls, crossword: Crossword, word: str) -> Word:
        if (word_coords := crossword.words_horizontal.get(word)) is not None:
            in_column = False
        elif (word_coords := crossword.words_vertical.get(word)) is not None:
            in_column = True
        else:
            raise WordNotFoundError(f"Word {word} not found in crossword")

        first_coord: tuple[int, int] = next(iter(word_coords))
        if in_column:
            index, _ = first_coord
        else:
            _, index = first_coord

        colrow = ColRow(crossword, in_column, index)
        return cls(crossword, colrow, word, word_coords)

    @classmethod
    def iter_from_crossword(cls, crossword: Crossword) -> Iterable[Word]:
        yield from (cls.from_crossword(crossword, word) for word in crossword.words)

    @classmethod
    def from_colrow(cls, colrow: ColRow, word: str) -> Word:
        return cls(colrow.crossword, colrow, word, colrow.crossword.words[word])

    def cross_words(self):
        yield from (
            Word.from_crossword(self.crossword, other_word)
            for other_word, other_letters in self.colrow.cross_words()
            if self.letter_fields & other_letters
        )

    @property
    def crossings(self):
        return self.letter_fields & self.crossword.crossings

    def cross_colrows(self):
        yield from (
            ColRow(self.crossword, not self.colrow.is_column, index)
            for index in self._get_indexes_of_crossing_colrows()
        )

    def die(self):
        if isinstance(self.crossword, CrosswordImprovable):
            self.crossword.remove(self.word)
        else:
            raise NotImplementedError("Removing words only available in CrosswordImprovable class")
