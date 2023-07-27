"""Defines ColRow class -- a reference to the given crossword column or row"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator

from ..commons.exceptions import PartNotFoundException
from ..commons.logger import logger
from ..commons.misc import Coord
from .base import Crossword


@dataclass(init=True, repr=True)
class ColRow:
    """A reference to the given crossword column or row, compatible with Crossword"""

    crossword: Crossword
    is_column: bool
    dim_num: int

    def get_coords(self) -> list[Coord]:
        """Returns `Coord` object in the given ColRow"""
        if self.is_column:
            max_v = getattr(self.crossword, "max_v", self.crossword.max[1])
            return [Coord((self.dim_num, i)) for i in range(max_v)]
        else:
            max_h = getattr(self.crossword, "max_h", self.crossword.max[0])
            return [Coord((i, self.dim_num)) for i in range(max_h)]

    def get(self) -> list[str | None]:
        """Returns list of letters in the given ColRow, Nones are inserted where no letter was found"""
        return [self.crossword.letters.get(i) for i in self.get_coords()]

    @property
    def is_full(self) -> bool:
        """Returns True if there is no None in the ColRow"""
        return None not in self.get()

    def __repr__(self) -> str:
        vals = "".join(i or ":" for i in self.get())
        return f"{'Col' if self.is_column else 'Row'}({self.dim_num}, {vals})"

    @staticmethod
    def _empty_slices(field_vals: list[str | None]) -> list[slice]:
        """Searches for big chunks of Nones in `field_vals` and returns their slices"""
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
        """Searches for big chunks of empty fields and returns their slices"""
        return self._empty_slices(self.get())

    @classmethod
    def _subparts(
        cls,
        fields: list[str | None],
        old_left_nones: int,
        old_right_nones: int,
    ):
        """
        Recursion that finds chunks of letters that can be used as queries, adds sorrounding Nones
        and yields the possible results. First the biggest chunks are yielded.

        Arguments:
            fields -- list of letters in fields (empty fields are represented using Nones)
            old_left_nones -- Number of nones that were to the left of the `fields` in the parent
            old_right_nones -- Number of nones that were to the right of the `fields` in the parent
        """
        slices = cls._empty_slices(fields)
        if len(slices) == 0:
            return
        biggest = max(slices, key=lambda x: x.stop - x.start)

        yield old_left_nones * [None] + fields[: biggest.start] + fields[biggest]
        yield fields[biggest] + fields[biggest.stop :] + old_right_nones * [None]
        yield from cls._subparts(fields[: biggest.start], old_left_nones, biggest.stop - biggest.start)
        yield from cls._subparts(fields[biggest.stop :], biggest.stop - biggest.start, old_right_nones)
        return

    def subparts(self):
        """
        Finds chunks of letters with sorrounding Nones, they can be used as queries.
        With every couple of yields, the chunks are separated by the biggest None group.

        ## Example

        Input: p _ _ k _ x _

        1. Yield: p _ _ k _ x _
        2. Find biggest gap between letters: p >_ _< k _ x _
        3. Divide and add the gap.
        4. Yield: p _ _
        5. Yield: _ _ k _ x _
        6. Repeat until slice length is 0
        """
        yield from self._subparts(self.get(), 0, 0)

    def yield_regexes(self) -> Iterator[str]:
        """Finds chunks of letters that can be used as queries and transforms them into regex"""
        found = set()
        for i in self.subparts():
            regex = self._regex_of_part(i)
            if regex not in found:
                found.add(regex)
                logger.debug("Found regex for {}: {}", self, regex)
                yield regex

    @staticmethod
    def _regex_of_part(part: list[str | None], letters_before: int = 0, letters_after: int = 0) -> str:
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
        """Finds best offset of a given word in ColRow."""
        field_vals = self.get()
        part_letters = list(enumerate(word))
        offsets = [
            i
            for i in range(len(field_vals) - len(word) + 1)
            if all(field_vals[n + i] is None or field_vals[n + i] == letter for n, letter in part_letters)
        ]
        found = max(
            offsets,
            key=lambda i: sum(field_vals[n + i] == letter for n, letter in part_letters),
            default=None,
        )
        if found is None:
            raise PartNotFoundException(f"Couldn't locate {word} in {field_vals}")
        else:
            return found

    def cross_words(self) -> Iterator[tuple[str, set[Coord]]]:
        """Yields words that colide with ColRow with their coordinate sets"""
        column, row = (self.dim_num, None) if self.is_column else (None, self.dim_num)
        for word, coords in self.crossword.words.items():
            columns, rows = tuple(zip(*coords))
            if column in set(columns) or row in set(rows):
                yield word, coords

    def removables(self) -> Iterator[tuple[str, int]]:
        """Yields words that can be removed from ColRow with their intersection count"""
        colrow_coords = set(self.get_coords())
        for word, colrows in self.crossword.words.items():
            if colrow_coords.issuperset(colrows):
                yield word, len(self.crossword.crossings.intersection(colrows))

    @staticmethod
    def iter(crossword: Crossword) -> Iterator[ColRow]:
        """Iterates over all ColRows of a crossword"""
        max_v = getattr(crossword, "max_v", crossword.max[1])
        max_h = getattr(crossword, "max_h", crossword.max[0])
        yield from (ColRow(crossword, False, i) for i in range(max_v))
        yield from (ColRow(crossword, True, i) for i in range(max_h))

    @staticmethod
    def iter_not_full(crossword: Crossword) -> Iterator[ColRow]:
        """Iterates over all ColRows of a crossword that are not full"""
        for i in ColRow.iter(crossword):
            if not i.is_full:
                yield i

    def __hash__(self) -> int:
        return hash((id(self.crossword), self.is_column, self.dim_num))