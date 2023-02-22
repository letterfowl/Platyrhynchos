from __future__ import annotations

from functools import cached_property
from itertools import groupby
from typing import Iterable, Optional
import re

from libs.crossword import Crossword
from libs.exceptions import TooLargeException, UninsertableException
from libs.utils import Coord, ProxiedDict, CruciverbalistDecision


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
            words_horizontal={word:{Coord((0, i)) for i in range(len(word))}},
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
            ProxiedDict(letters, on_set=lambda key,
                        _: self.checkSize(key[0], key[1])),
            words_horizontal,
            words_vertical,
            crossings,
        )

    def __repr__(self) -> str:
        size = self.max
        max_size = self.max_h, self.max_v
        return "\n".join(
            "".join(
                (
                    self.letters.get(Coord((h, v)), ":")
                    for h in range(self.max_h)
                )
            )
            for v in range(self.max_v)
        )# + f"\n[{size=} {max_size=}]"

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
        while pattern[-1]==".":
            pattern.pop(-1)
            added_optional.append(".?")
        return "("+")(".join(pattern+added_optional)+")"

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

    def add(self, word: str, is_column: bool, to: int):
        """
        Adds a word to the crossword row/column. It requires an intersection.

        Arguments:
            word -- word to add
            is_column -- True if n is column ID
            to -- column/row id
        
        ```
        >>> c = CrosswordImprovable.make("dupa", 4, 4)
        >>> c.add("peja", True, 2)
        >>> print(c)
        dupa
        ::e:
        ::j:
        ::a:
        
        >>> c.add("co", True, 3)
        Traceback (most recent call last):
            ...
        libs.exceptions.UninsertableException: word='co'; reg2='(a)(.?)(.?)(.?)'; no match
        
        >>> c.add("ej", False, 2)
        >>> print(c)
        dupa
        ::e:
        :ej:
        ::a:
        
        ```

        Raises:
            UninsertableException: no match - Regex couldn't find a match
            UninsertableException: no group found - regex didn't find a group (weird)
        """
        _, reg2 = self.regexes(is_column, to)
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
            pos = Coord((to, place)) if is_column else Coord((place, to))
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
        else:
            if self.letters[coord] != letter:
                raise UninsertableException(f"This field is already occupied ({coord=}; new={letter}; old={self.letters[coord]})")
            self.crossings.add(coord)

    def handle_decision(self, decision: CruciverbalistDecision):
        is_column, n, word = decision
        self.add(word, is_column, n)