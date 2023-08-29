"""Defines ColRow class -- a reference to the given crossword column or row"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Generator

from ..commons.exceptions import PartNotFoundException
from ..commons.logger import logger
from ..commons.misc import ColRowId, ColRowIndex, Coord, IsColumn
from ..commons.utils import random
from .base import Crossword


@dataclass(init=True, repr=True)
class ColRow:
    """
    A reference to the given crossword column or row, compatible with Crossword

    `ColRow(crossword, True, 0)` is the first column of the crossword ((0, 0), (0, 1), (0, 2), ...)
    `ColRow(crossword, False, 0)` is the first row of the crossword ((0, 0), (1, 0), (2, 0), ...)
    """

    crossword: Crossword
    is_column: bool
    index: int

    @classmethod
    def from_coord(cls, crossword: Crossword, coord: Coord) -> tuple[ColRow, ColRow]:
        """Returns the column and row of the given Coord"""
        return (cls(crossword, True, coord[0]), cls(crossword, False, coord[1]))

    def get_coords(self) -> list[Coord]:
        """Returns `Coord` object in the given ColRow"""
        return [self.get_coord(i) for i in self.coord_indexes()]

    def coord_indexes(self) -> list[int]:
        """Returns indexes of the `Coord` objects in the given ColRow"""
        max_h, max_v = self.crossword.max
        return list(range(max_v)) if self.is_column else list(range(max_h))

    def coord_index(self, coord: Coord) -> int:
        """Returns the index of the given `Coord` in the given `ColRow`"""
        return coord[1] if self.is_column else coord[0]

    def get_coord(self, index: int) -> Coord:
        """Returns the `Coord` in the given `ColRow` with the given index"""
        if self.is_column:
            return Coord((self.index, index))
        else:
            return Coord((index, self.index))

    def offset(self, offset: int) -> ColRow:
        """Returns a ColRow with an offset of `offset`"""
        return ColRow(self.crossword, self.is_column, self.index + offset)

    @property
    def length(self) -> int:
        return self.crossword.max[1 if self.is_column else 0]

    def get(self) -> list[str | None]:
        """Returns list of letters in the given ColRow, Nones are inserted where no letter was found"""
        return [self.crossword.letters.get(i) for i in self.get_coords()]

    @property
    def is_full(self) -> bool:
        """Returns True if there is no None in the ColRow"""
        return None not in self.get()

    def __repr__(self) -> str:
        vals = "".join(i or ":" for i in self.get())
        return f"{'Col' if self.is_column else 'Row'}({self.index}, {vals})"

    def history_id(self) -> ColRowId:
        """Returns a unique id of the ColRow for a crossword generation task (used in history)"""
        return (IsColumn(self.is_column), ColRowIndex(self.index))

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
        yield from cls._subparts(
            fields[: biggest.start], old_left_nones, biggest.stop - biggest.start
        )
        yield from cls._subparts(
            fields[biggest.stop :], biggest.stop - biggest.start, old_right_nones
        )
        return

    def get_for_subparts(self) -> Generator[list[str | None], None, None]:
        yield from self.crossword.get_for_subparts(self.history_id())

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
        for i in self.get_for_subparts():
            yield from self._subparts(i, 0, 0)

    def yield_regexes(self) -> Generator[str, None, None]:
        """Finds chunks of letters that can be used as queries and transforms them into regex"""
        found = set()
        for i in self.subparts():
            regex = self._regex_of_part(i)
            if regex not in found:
                found.add(regex)
                logger.debug("Found regex for {}: {}", self, regex)
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
        """Finds best offset of a given word in ColRow."""
        if hasattr(self.crossword, "get_reserved_fields_in_colrow"):
            excluded: set[Coord] = self.crossword.get_reserved_fields_in_colrow(self)  # type: ignore
        else:
            excluded = set()

        field_vals = self.get()
        part_letters = list(enumerate(word))

        possible_offsets: list[int] = []
        for i in range(len(field_vals) - len(word) + 1):
            if all(
                field_vals[n + i] is None or field_vals[n + i] == letter
                for n, letter in part_letters
            ):
                if all((self.get_coord(n + i) not in excluded for n, letter in part_letters)):
                    possible_offsets.append(i)

        found = random.choices(
            possible_offsets,
            [
                1 + sum(field_vals[n + i] == letter for n, letter in part_letters)
                for i in possible_offsets
            ],
            k=1,
        )
        if len(found) == 0:
            raise PartNotFoundException(f"Couldn't locate {word} in {field_vals}")
        else:
            return found[0]

    def cross_words(self) -> Generator[tuple[str, set[Coord]], None, None]:
        """Yields words that colide with ColRow with their coordinate sets"""
        column, row = (self.index, None) if self.is_column else (None, self.index)
        for word, coords in self.crossword.words.items():
            columns, rows = tuple(zip(*coords))
            if column in set(columns) or row in set(rows):
                yield word, coords

    def in_words(self) -> Generator[tuple[str, set[Coord]], None, None]:
        """Yields words that colide with ColRow with their coordinate sets"""
        column, row = (None, self.index) if self.is_column else (self.index, None)
        for word, coords in self.crossword.words.items():
            columns, rows = tuple(zip(*coords))
            if column in set(columns) or row in set(rows):
                yield word, coords

    def removables(self) -> Generator[tuple[str, int], None, None]:
        """Yields words that can be removed from ColRow with their intersection count"""
        colrow_coords = set(self.get_coords())
        for word, colrows in self.crossword.words.items():
            if colrow_coords.issuperset(colrows):
                yield word, len(self.crossword.crossings.intersection(colrows))

    @staticmethod
    def iter(crossword: Crossword) -> Generator[ColRow, None, None]:
        """Iterates over all ColRows of a crossword"""
        max_v = getattr(crossword, "max_v", crossword.max[1])
        max_h = getattr(crossword, "max_h", crossword.max[0])
        yield from (ColRow(crossword, False, i) for i in range(max_v))
        yield from (ColRow(crossword, True, i) for i in range(max_h))

    @staticmethod
    def iter_not_full(crossword: Crossword) -> Generator[ColRow, None, None]:
        """Iterates over all ColRows of a crossword that are not full"""
        for i in ColRow.iter(crossword):
            if not i.is_full:
                yield i

    def __hash__(self) -> int:
        return hash((id(self.crossword), self.is_column, self.index))
