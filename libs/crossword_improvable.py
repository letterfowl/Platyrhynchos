from __future__ import annotations

from functools import cached_property
from itertools import groupby
from typing import Iterable, Iterator, Optional
import re

from libs.crossword import Crossword
from libs.exceptions import (
    PartNotFoundException,
    TooLargeException,
    UninsertableException,
)
from libs.utils import Coord, ProxiedDict, CruciverbalistDecision, find_sub_list


class CrosswordImprovable(Crossword):
    @staticmethod
    def make(word: str, max_h: int, max_v: Optional[int] = None) -> CrosswordImprovable:
        """
        Should create a one word crossword. For example:

        ```
        >>> print(CrosswordImprovable.make("dupa", 10, 4))
        dupa::::::
        ::::::::::
        ::::::::::
        ::::::::::

        >>> print(CrosswordImprovable.make("dupa", 4, 1))
        dupa

        ```

        Arguments:
            word -- word to add
            max_h -- maximum columns
            max_v -- maximum rows (default: {None})
        """
        max_v = max_v or max_h
        return CrosswordImprovable(
            letters={Coord((i, 0)): j for i, j in enumerate(word)},
            max_h=max_h,
            max_v=max_v,
            words_horizontal={word: {Coord((0, i)) for i in range(len(word))}},
        )

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
            ProxiedDict(letters, on_set=lambda key, _: self.checkSize(key[0], key[1])),
            words_horizontal,
            words_vertical,
            crossings,
        )

    def __repr__(self) -> str:
        size = self.max
        max_size = self.max_h, self.max_v
        return "\n".join(
            "".join((self.letters.get(Coord((h, v)), ":") for h in range(self.max_h)))
            for v in range(self.max_v)
        )  # + f"\n[{size=} {max_size=}]"

    def rotate(self):
        """
        Rotates the crossword, works in place.

        ```
        >>> c = CrosswordImprovable.make("dupa", 4, 1)
        >>> c.rotate()
        >>> print(c)
        d
        u
        p
        a

        >>> c.rotate()
        >>> print(c)
        dupa

        ```
        It will do that by swapping column and row ids and `rows_vertical` with `rows_horizontal` (while also changing the ids in them):
        ```
        >>> c = CrosswordImprovable({(0,1):'a'}, 2, 2, words_horizontal={'a':{(0,1)}}, crossings = {(0,1)})
        >>> c.rotate()
        >>> c.crossings
        {(1, 0)}
        >>> c.words_vertical
        {'a': {(1, 0)}}
        >>> c.words_horizontal
        {}
        """
        self.letters = {
            Coord((j, i)): letter for (i, j), letter in self.letters.items()
        }
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
        return "".join(re.escape(i) if i is not None else else_str for i in letters)

    @staticmethod
    def _combine_rere(letters):
        pattern = []
        empty = True
        for i in letters:
            if i is None:
                pattern.append(".?" if empty else ".")
            else:
                pattern.append(re.escape(i))
                empty = False

        added_optional = []
        while pattern[-1] == ".":
            pattern.pop(-1)
            added_optional.append(".?")
        return "(" + ")(".join(pattern + added_optional) + ")"

    def regexes(self, is_column: bool, n: int):
        if is_column:
            letters = [self.letters.get(Coord((n, i))) for i in range(self.max_v)]
        else:
            letters = [self.letters.get(Coord((i, n))) for i in range(self.max_h)]
        return self._combine_re(letters), self._combine_rere(letters)

    @cached_property
    def columns(self):
        return dict(groupby(self.letters.keys(), key=lambda x: x[0]))

    @cached_property
    def rows(self):
        return dict(groupby(self.letters.keys(), key=lambda x: x[-1]))

    def get_with_empty(self, dim_val: int, is_column: bool) -> list[str | None]:
        if is_column:
            return [self.letters.get(Coord((dim_val, i))) for i in range(self.max_v)]
        else:
            return [self.letters.get(Coord((i, dim_val))) for i in range(self.max_h)]

    def yield_regexes(self, dim_val: int, is_column: bool) -> Iterator[str]:
        """
        >>> c = CrosswordImprovable({(0,1):'a', (2,1):'b', (4,1):'s', (1,1):'g'}, 10, 10, words_horizontal={'a':{(0,1)}}, crossings = {(0,1)})
        >>> list(c.yield_regexes(0, True))
        ['^.{0,1}a.{0,8}$', '^.{0,8}$', '^.{0,1}$']

        >>> list(c.yield_regexes(1, False))
        ['^agb.{1}s.{0,5}$', '^.{0,5}$', '^agb.{0,1}$', '^.{0,1}s.{0,5}$']
        """
        letters = self.get_with_empty(dim_val, is_column)
        found = set()
        for i in self._letters_subparts(letters):
            regex = self._regex_of_part(i)
            if regex not in found:
                found.add(regex)
                yield regex

    @staticmethod
    def _find_empties(column_row: list[str | None]) -> list[slice]:
        begin = None
        slices = []
        for ith, i in enumerate(column_row):
            if i is not None:
                if begin is not None:
                    slices.append(slice(begin, ith))
                begin = None
            elif begin is None:
                begin = ith

        if begin is not None:
            slices.append(slice(begin, len(column_row)))
        return slices

    @classmethod
    def _letters_subparts(
        cls,
        column_row: list[str | None],
        old_left_nones: int = 0,
        old_right_nones: int = 0,
    ):
        slices = cls._find_empties(column_row)
        if len(slices) == 0:
            return
        biggest = max(slices, key=lambda x: x.stop - x.start)

        yield old_left_nones * [None] + column_row[: biggest.start] + column_row[
            biggest
        ]
        yield column_row[biggest] + column_row[biggest.stop :] + old_right_nones * [
            None
        ]
        yield from cls._letters_subparts(
            column_row[: biggest.start], old_left_nones, biggest.stop - biggest.start
        )
        yield from cls._letters_subparts(
            column_row[biggest.stop :], biggest.stop - biggest.start, old_right_nones
        )
        return

    @staticmethod
    def _regex_of_part(
        part: list[str | None], letters_before: int = 0, letters_after: int = 0
    ) -> str:
        """
        Generates the regex of a row/column part. For example:

        TODO: Add tests

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

    def _pos_of_word(self, word: str, dim_val: int, is_column: bool) -> int:
        column_row = self.get_with_empty(dim_val, is_column)
        part_letters = list(enumerate(word))
        for i in range(len(column_row) - len(word) + 1):
            if all(
                column_row[n + i] == letter
                for n, letter in part_letters
                if letter in column_row
            ):
                return i
        raise PartNotFoundException(f"Couldn't locate {word} in {column_row}")

    def cross_words(
        self, dim_val: int, is_column: bool
    ) -> Iterable[tuple[str, set[Coord]]]:
        column, row = (dim_val, None) if is_column else (None, dim_val)
        for word, coords in self.words.items():
            columns, rows = tuple(zip(*coords))
            if column in set(columns) or row in set(rows):
                yield word, coords

    def add(self, word: str, is_column: bool, dim_val: int):
        """
        Adds a word to the crossword row/column. It requires an intersection.

        Arguments:
            word -- word to add
            part -- sublist used to find this word
            is_column -- True if n is column ID
            dim_val -- column/row id

        ```
        >>> c = CrosswordImprovable.make("dupa", 4, 4)
        >>> c.add("peja", True, 2)
        >>> print(c)
        dupa
        ::e:
        ::j:
        ::a:

        >>> c.add("ej", False, 2)
        >>> print(c)
        dupa
        ::e:
        :ej:
        ::a:

        >>> c.add("co", False, 3)
        >>> print(c)
        dupa
        ::e:
        :ej:
        coa:

        ```
        """
        start_index = self._pos_of_word(word, dim_val, is_column)
        if is_column:
            self.words_vertical[word] = set()
        else:
            self.words_horizontal[word] = set()

        for place, letter in enumerate(word, start_index):
            pos = Coord((dim_val, place)) if is_column else Coord((place, dim_val))
            self.add_letter(pos, letter)

            if is_column:
                self.words_vertical[word].add(pos)
            else:
                self.words_horizontal[word].add(pos)

    def add_letter(self, coord: Coord, letter: str):
        """
        Add a letter to the crossword, unless the crossword already contains it at this coordinate. Then a crossing will be added. For example:

        ```
        >>> c = CrosswordImprovable.make("dupa", 4, 4)
        >>> c.add_letter((3,3), 'g')
        >>> print(c)
        dupa
        ::::
        ::::
        :::g

        >>> c.add_letter((3,3), 'g')
        >>> print(c)
        dupa
        ::::
        ::::
        :::g
        >>> c.crossings
        {(3, 3)}

        >>> c.add_letter((0,0), 'g')
        Traceback (most recent call last):
            ...
        libs.exceptions.UninsertableException: This field is already occupied (coord=(0, 0); new=g; old=d)

        ```

        Arguments:
            coord -- Coordinates
            letter -- The letter to add
        """
        if coord not in self.letters:
            self.letters[coord] = letter
        elif self.letters[coord] == letter:
            self.crossings.add(coord)
        else:
            raise UninsertableException(
                f"This field is already occupied ({coord=}; new={letter}; old={self.letters[coord]})"
            )

    # def handle_decision(self, decision: CruciverbalistDecision):
    #     is_column, n, word = decision
    #     self.add(word, is_column, n)
