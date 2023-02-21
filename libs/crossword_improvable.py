from __future__ import annotations

from functools import cached_property
from itertools import groupby
from typing import Iterable, Optional
import re

from .crossword import Crossword
from .exceptions import TooLargeException, UninsertableException
from .utils import Coord, ProxiedDict


class CrosswordImprovable(Crossword):
    def checkSize(self, x: int, y: int):
        if x >= self.max_h or y >= self.max_v:
            raise TooLargeException(
                f"{x=} while {self.max_h=}; {y=} while {self.max_v=}"
            )

    def __init__(
        self,
        letters: dict[Coord, str],
        max_h: int,
        max_v: int,
        words_horizontal: dict[str, set[Coord]],
        words_vertical: Optional[dict[str, set[Coord]]] = None,
        crossings: Optional[set[Coord]] = None,
    ):
        self.max_h = max_h
        self.max_v = max_v
        words_vertical = words_vertical or {}
        crossings = crossings or set()
        super().__init__(
            ProxiedDict(letters, on_set=lambda key,
                        _: self.checkSize(key[0], key[1])),
            words_horizontal,
            words_vertical,
            crossings,
        )

    def rotate(self):
        self.letters = {Coord((j, i)): letter for (
            i, j), letter in self.letters.items()}
        self.max_h, self.max_v = self.max_v, self.max_h
        new_horizontal = {
            word: {Coord((h, v)) for (v, h) in i}
            for word, i in self.words_vertical.items()
        }
        new_vertical = {
            word: {Coord((h, v)) for (v, h) in i}
            for word, i in self.words_horizontal.items()
        }
        self.words_horizontal, self.words_vertical = new_horizontal, new_vertical
        self.crossings = {Coord((j, i)) for (i, j) in self.crossings}

    @staticmethod
    def _combine_re(letters, else_str=".?"):
        return "".join(
            re.escape(i)
            if i is not None else else_str
            for i in letters
        )

    @staticmethod
    def _combine_rere(letters, else_str=".?"):
        return "("+")(".join(
            re.escape(i)
            if i is not None else else_str
            for i in letters
        )+")"

    def regexes(self, is_column: bool, n: int):
        if is_column:
            letters = [
                self.letters.get(Coord((n, i))) for i in range(self.max_v)
            ]
        else:
            letters = [
                self.letters.get(Coord((i, n))) for i in range(self.max_h)
            ]
        return self._combine_re(letters), self._combine_rere(letters)

    @cached_property
    def columns(self):
        return groupby(self.letters.keys(), key=lambda x: x[0])

    @cached_property
    def rows(self):
        return groupby(self.letters.keys(), key=lambda x: x[-1])

    def cross_words(self, n: int, is_column: bool) -> Iterable[tuple[str, set[Coord]]]:
        column, row = (n, None) if is_column else (None, n)
        for word, coords in self.words.items():
            columns, rows = tuple(zip(*coords))
            if column in set(columns) or row in set(rows):
                yield word, coords

    def add(self, word: str, is_column: bool, n: int):
        _, reg2 = self.regexes(is_column, n)
        matched = re.match(reg2, word)
        if matched is None:
            raise UninsertableException(f"{word=}; {reg2=}; no match")
        for n, l in enumerate(matched.groups()):
            if l != "":
                from_zero = n
                break
        else:
            raise UninsertableException(f"{word=}; {reg2=}; no group found")

        if is_column:
            self.words_vertical[word] = set()
        else:
            self.words_horizontal[word] = set()

        for place, letter in enumerate(word, from_zero):
            pos = Coord((n, place)) if is_column else Coord((place, n))
            self.add_letter(pos, letter)

            if is_column:
                self.words_vertical[word].add(pos)
            else:
                self.words_horizontal[word].add(pos)

    def add_letter(self, coord: Coord, letter: str):
        if coord not in self.letters:
            self.letters[coord] = letter
        else:
            self.crossings.add(coord)
