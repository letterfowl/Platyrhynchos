from __future__ import annotations

from typing import Optional, Iterator, NoReturn

from .colrow import ColRow
from .crossword import Crossword
from .exceptions import TooLargeException, UninsertableException
from .commons import ColRowId, Coord, IsColumn, ProxiedDict


class CrosswordImprovable(Crossword):
    """
    Crossword subclass used to implement the "smart" insertion algorithm.
    """

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

    def check_size(self, horizontal: int, vertical: int) -> NoReturn | None:
        """
        Compares size of crossword with provided arguments

        + ---> horizontal
        |
        ⌄ vertical

        Raises:
            TooLargeException: coordinates don't fit into the crossword
        """
        if horizontal >= self.max_h or vertical >= self.max_v:
            raise TooLargeException(
                f"{horizontal=} vs {self.max_h}; {vertical=} vs {self.max_v}"
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
            ProxiedDict(letters, on_set=lambda key, _: self.check_size(key[0], key[1])),
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

    def colrow(self, is_column: IsColumn, nth: ColRowId) -> ColRow:
        """
        Gets ColRow object

        Arguments:
            is_column -- Bool telling whether you want to retrieve a column (True) or row (False)
            nth -- used to determine which to retrieve (it will take the nth one)

        Returns:
            ColRow object
        """
        colrow = ColRow(self, is_column, nth)
        for i, j in colrow.get_coords():
            self.check_size(i, j)
        return colrow

    def iter_colrows(self) -> Iterator[ColRow]:
        yield from ColRow.iter(self)

    def add(self, word: str, colrow: ColRow | tuple[IsColumn, ColRowId]):
        """
        Adds a word to the crossword row/column. It requires a possible intersection.

        Arguments:
            word -- word to add
            part -- sublist used to find this word
            is_column -- True if n is column ID
            dim_val -- column/row id

        """
        if not isinstance(colrow, ColRow):
            colrow = self.colrow(colrow[0], colrow[-1])
        start_index = colrow.pos_of_word(word)

        new_word = {word: set()}
        old_letters = self.letters.copy()
        old_crossings = self.crossings.copy()

        try:
            for place, letter in enumerate(word, start_index):
                pos = (
                    Coord((colrow.dim_num, place))
                    if colrow.is_column
                    else Coord((place, colrow.dim_num))
                )
                self.add_letter(pos, letter)

                new_word[word].add(pos)
        except UninsertableException as exception:
            self.letters = old_letters
            self.crossings = old_crossings
            raise exception
        else:
            if colrow.is_column:
                self.words_vertical |= new_word
            else:
                self.words_horizontal |= new_word

    def add_letter(self, coord: Coord, letter: str):
        """
        Add a letter to the crossword, unless the crossword already contains it at this coordinate. Then a crossing will be added.

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
