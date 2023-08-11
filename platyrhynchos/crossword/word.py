"""Word wrapper over the ColRow and CrosswordImprovable class"""
from __future__ import annotations
from dataclasses import dataclass

from .improvable import CrosswordImprovable
from .colrow import ColRow
from ..commons.misc import Coord
from ..commons.exceptions import WordNotFoundError

@dataclass
class Word:
    crossword: CrosswordImprovable
    colrow: ColRow
    word: str
    letters: set[Coord]

    @classmethod
    def from_crossword(cls, crossword: CrosswordImprovable, word: str) -> Word:
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

    def cross_words(self):
        yield from (
            Word.from_crossword(self.crossword, other_word)
            for other_word, other_letters in self.colrow.cross_words() if self.letters & other_letters
        )

    @property
    def crossings(self):
        return self.letters & self.crossword.crossings

    def cross_colrows(self):
        yield from (
            i.colrow for i in self.cross_words()
        )