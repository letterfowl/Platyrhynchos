"""Implements the improvable crossword class"""
from __future__ import annotations

from contextlib import suppress
from typing import Callable, Iterator, NoReturn, Optional

from ..commons.exceptions import TooLargeException, UninsertableException
from ..commons.misc import ColRowIndex, Coord, IsColumn, ProxiedDict
from .base import Crossword
from .colrow import ColRow
from .exolve_template import EXOLVE_TEMPLATE, Template, char_for_grid

EXOLVE_TEMPLATE: Template


class CrosswordImprovable(Crossword):
    """Crossword subclass used to implement the "smart" insertion algorithm."""

    @classmethod
    def make(
        cls, word: str, max_h: int, max_v: Optional[int] = None
    ) -> CrosswordImprovable:
        """
        Creates a one word crossword.

        Arguments:
            word -- word to add
            max_h -- maximum columns
            max_v -- maximum rows (default: {None})
        """
        max_v = max_v or max_h
        return cls(
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
        if horizontal > self.max_h or vertical > self.max_v:
            raise TooLargeException(
                f"h={horizontal} vs max_h={self.max_h}; v={vertical} vs max_v={self.max_v}"
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
        """
        Creates a crossword while ensuring all letters can be contained in the max sizes

        Arguments:
            letters -- mapping from coords to letters
            max_h -- Max horizontal
            max_v -- Max vertical
            words_horizontal -- mapping of words to sets of coordinates in the horizontal axis

        Keyword Arguments:
            words_vertical -- mapping of words to sets of coordinates in the vertical axis (default: {None})
            crossings -- Set of all crossings in the crossword (default: {None})
        """
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

    def as_exolve_grid(
        self,
        empty_field: str = ":",
        sep: str = "\n",
        coder: Callable[[str], str] = lambda x: x,
    ) -> str:
        """Returns a grid representation of the crossword"""

        return sep.join(
            "".join(
                (
                    coder(self.letters.get(Coord((h, v)), empty_field))
                    for h in range(self.max_h)
                )
            )
            for v in range(self.max_v)
        )

    def print_rich_grid(self):
        try:
            from rich import print as rich_print

            def _get_coord(h, v):
                coord = Coord((h, v))
                v = self.letters.get(coord, "[gray]:[/gray]")
                if coord in self.crossings:
                    v = f"[green]{v}[/green]"
                return v

            rich_print(
                "\n".join(
                    "".join(_get_coord(h, v) for h in range(self.max_h))
                    for v in range(self.max_v)
                )
            )
        except ImportError:
            print(self.as_exolve_grid())

    def as_exolve(self) -> str:
        """
        Returns an exolve representation of the crossword. Go to `exolve_template.py` for the template.

        """
        # pylint: disable=unpacking-non-sequence
        size_x, size_y = self.max
        return EXOLVE_TEMPLATE.substitute(
            width=size_x,
            height=size_y,
            grid=self.as_exolve_grid(
                empty_field=".", sep="\n    ", coder=char_for_grid
            ),
        )

    @property
    def max(self):
        return self.max_h, self.max_v

    def __repr__(self) -> str:
        # size = self.max
        # max_size = self.max_h, self.max_v
        return self.as_exolve_grid()  # + f"\n[{size=} {max_size=}]"

    def rotate(self):
        """Rotates the crossword, works in place."""
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

    def colrow(self, is_column: IsColumn, nth: ColRowIndex) -> ColRow:
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
        """Iterate over all colrows in the crossword."""
        yield from ColRow.iter(self)

    def iter_not_full_colrows(self) -> Iterator[ColRow]:
        """Iterate over all colrows in the crossword that are not full."""
        yield from ColRow.iter_not_full(self)

    def get_future_word_coords(self, word: str, colrow: ColRow) -> dict[Coord, str]:
        """
        Given a word and a ColRow object, returns a potential dictionary of the coordinates and letters of the word in the ColRow object.

        Args:
        - word (str): The word to find in the ColRow object.
        - colrow (ColRow): The ColRow object to search for the word in.

        Returns:
        - dict[Coord, str]: A dictionary where the keys are the coordinates of each letter in the word, and the values are the letters themselves.
        """
        start_index = colrow.pos_of_word(word)

        indexes = ((start_index + i, letter) for i, letter in enumerate(word))
        if colrow.is_column:
            return {Coord((colrow.index, index)): letter for index, letter in indexes}
        else:
            return {Coord((index, colrow.index)): letter for index, letter in indexes}

    def add(self, word: str, colrow: ColRow | tuple[IsColumn, ColRowIndex]):
        """
        Adds a word to the crossword row/column. It requires a possible intersection. Works in place.

        Arguments:
            word -- word to add
            part -- sublist used to find this word
            is_column -- True if n is column ID
            dim_val -- column/row id

        """
        if not isinstance(colrow, ColRow):
            colrow = self.colrow(colrow[0], colrow[-1])

        letters_to_add = self.get_future_word_coords(word, colrow)
        new_word = {word: set(letters_to_add.keys())}
        old_letters = self.letters.copy()
        old_crossings = self.crossings.copy()

        try:
            for pos, letter in letters_to_add.items():
                self.add_letter(pos, letter)
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
        Add a letter to the crossword, unless the crossword already contains it at this coordinate.
        Then a crossing will be added. Works in place.

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

    def remove(self, word: str) -> Optional[CrosswordImprovable]:
        letter_coords = self.words.get(word, None)
        if letter_coords is None:
            raise ValueError(f"Word {word} not found in {self.words}")
        new = self.__class__(
            letters={
                coord: i
                for coord, i in self.letters.items()
                if coord not in letter_coords or coord in self.crossings
            },
            max_h=self.max_h,
            max_v=self.max_v,
            words_vertical={w: i for w, i in self.words_vertical.items() if word != w},
            words_horizontal={
                w: i for w, i in self.words_horizontal.items() if word != w
            },
            crossings={
                coords for coords in self.crossings if coords not in letter_coords
            },
        )
        return None if len(new.words) == 0 else new
