from __future__ import annotations

from typing import Optional, Iterator

from .colrow import ColRow
from .crossword import Crossword
from .exceptions import TooLargeException, UninsertableException
from .utils import ColRowId, Coord, IsColumn, ProxiedDict


class CrosswordImprovable(Crossword):
    @staticmethod
    def make(word: str, max_h: int, max_v: Optional[int] = None) -> CrosswordImprovable:
        """
        Should create a one word crossword.

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
        # size = self.max
        # max_size = self.max_h, self.max_v
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

    def colrow(self, is_column: IsColumn, colrow: ColRowId):
        return ColRow(self, is_column, colrow)
    
    def iter_colrows(self) -> Iterator[ColRow]:
        yield from ColRow.iter(self)

    def add(self, word: str, colrow: ColRow | tuple[IsColumn, ColRowId]):
        """
        Adds a word to the crossword row/column. It requires an intersection.

        Arguments:
            word -- word to add
            part -- sublist used to find this word
            is_column -- True if n is column ID
            dim_val -- column/row id

        ```
        >>> c = CrosswordImprovable.make("dupa", 4, 4)
        >>> c.add("peja", (True, 2))
        >>> print(c)
        dupa
        ::e:
        ::j:
        ::a:

        >>> c.add("ej", (False, 2))
        >>> print(c)
        dupa
        ::e:
        :ej:
        ::a:

        >>> c.add("co", (False, 3))
        >>> print(c)
        dupa
        ::e:
        :ej:
        coa:

        ```
        """
        if not isinstance(colrow, ColRow):
            colrow = self.colrow(colrow[0], colrow[-1])
        start_index = colrow.pos_of_word(word)
        if colrow.is_column:
            self.words_vertical[word] = set()
        else:
            self.words_horizontal[word] = set()

        for place, letter in enumerate(word, start_index):
            pos = (
                Coord((colrow.dim_num, place))
                if colrow.is_column
                else Coord((place, colrow.dim_num))
            )
            self.add_letter(pos, letter)

            if colrow.is_column:
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