from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator

from .base import Crossword

from ..commons.exceptions import PartNotFoundException
from ..commons.misc import Coord


@dataclass(init=True, repr=True)
class ColRow:
    crossword: Crossword
    is_column: bool
    dim_num: int

    def get_coords(self) -> list[Coord]:
        if self.is_column:
            max_v = getattr(self.crossword, "max_v", self.crossword.max[1])
            return [Coord((self.dim_num, i)) for i in range(max_v)]
        else:
            max_h = getattr(self.crossword, "max_h", self.crossword.max[0])
            return [Coord((i, self.dim_num)) for i in range(max_h)]

    def get(self) -> list[str | None]:
        return [self.crossword.letters.get(i) for i in self.get_coords()]

    def __repr__(self) -> str:
        vals = "".join(i or ":" for i in self.get())
        return f"{'Col' if self.is_column else 'Row'}({self.dim_num}, {vals})"

    @staticmethod
    def _empty_slices(field_vals: list[str | None]) -> list[slice]:
        begin = None
        slices = []
        for ith, i in enumerate(field_vals):
            if i is not None:
                if begin is not None:
                    slices.append(slice(begin, ith))
                begin = None
            elif begin is None:
                begin = ith

        if begin is not None:
            slices.append(slice(begin, len(field_vals)))
        return slices

    def empty_slices(self) -> list[slice]:
        return self._empty_slices(self.get())

    @classmethod
    def _subparts(
        cls,
        column_row: list[str | None],
        old_left_nones: int,
        old_right_nones: int,
    ):
        slices = cls._empty_slices(column_row)
        if len(slices) == 0:
            return
        biggest = max(slices, key=lambda x: x.stop - x.start)

        yield old_left_nones * [None] + column_row[: biggest.start] + column_row[
            biggest
        ]
        yield column_row[biggest] + column_row[biggest.stop :] + old_right_nones * [
            None
        ]
        yield from cls._subparts(
            column_row[: biggest.start], old_left_nones, biggest.stop - biggest.start
        )
        yield from cls._subparts(
            column_row[biggest.stop :], biggest.stop - biggest.start, old_right_nones
        )
        return

    def subparts(self, old_left_nones: int = 0, old_right_nones: int = 0):
        yield from self._subparts(self.get(), old_left_nones, old_right_nones)

    def yield_regexes(self) -> Iterator[str]:
        found = set()
        for i in self.subparts():
            regex = self._regex_of_part(i)
            if regex not in found:
                found.add(regex)
                yield regex

    @staticmethod
    def _regex_of_part(
        part: list[str | None], letters_before: int = 0, letters_after: int = 0
    ) -> str:
        """
        Generates the regex of a row/column part. For example:

        Arguments:
            part -- Part of get_with_empty result (or full result)
            letters_before -- number of letters allowed before the part (defaults to 0)
            letters_after -- number of letters allowed after the part (defaults to 0)

        Returns:
            Regex string
        """
        reg_list = []
        none_series = 0
        for i in part:
            if i is None:
                none_series += 1
            else:
                # reset Nones
                if not reg_list:
                    letters_before += none_series
                elif none_series > 0:
                    reg_list.append(".{%s}" % none_series)
                none_series = 0

                # add current
                reg_list.append(re.escape(i))
        letters_after += none_series

        reg_list = [
            "^",
            ".{0,%s}" % letters_before,
            *reg_list,
            ".{0,%s}" % letters_after,
            "$",
        ]
        reg_list = [i for i in reg_list if i not in {".{0}", ".{0,0}"}]
        return "".join(reg_list)

    def pos_of_word(self, word: str) -> int:
        field_vals = self.get()
        part_letters = list(enumerate(word))
        offsets = [
            i
            for i in range(len(field_vals) - len(word) + 1)
            if all(
                field_vals[n + i] is None or field_vals[n + i] == letter
                for n, letter in part_letters
            )
        ]
        found = max(
            offsets,
            key=lambda i: sum(
                field_vals[n + i] == letter for n, letter in part_letters
            ),
            default=None,
        )
        if found is None:
            raise PartNotFoundException(f"Couldn't locate {word} in {field_vals}")
        else:
            return found

    def cross_words(self) -> Iterator[tuple[str, set[Coord]]]:
        column, row = (self.dim_num, None) if self.is_column else (None, self.dim_num)
        for word, coords in self.crossword.words.items():
            columns, rows = tuple(zip(*coords))
            if column in set(columns) or row in set(rows):
                yield word, coords

    @staticmethod
    def iter(crossword: Crossword) -> Iterator[ColRow]:
        max_v = getattr(crossword, "max_v", crossword.max[1])
        max_h = getattr(crossword, "max_h", crossword.max[0])
        yield from (ColRow(crossword, False, i) for i in range(max_v))
        yield from (ColRow(crossword, True, i) for i in range(max_h))
