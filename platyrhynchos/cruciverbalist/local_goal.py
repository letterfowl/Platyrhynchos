"""
This module contains an abstract Cruciverbalist based on approximating the goal value for each field.
"""

from abc import ABC, abstractmethod
from typing import Iterator
from ..crossword.base import Crossword
from ..commons.misc import Coord
from ..commons.utils import random
from ..crossword.colrow import ColRow
from ..crossword.word import Word


def avg(iterable):
    """
    Calculates the average of an iterable.

    Args:
    iterable: An iterable object.

    Returns:
    The average of the iterable.
    """
    return sum(iterable) / len(iterable)


class LocalGoalCruciverbalistBase(ABC):
    """
    An abstract Cruciverbalist based on approximating the goal value for each field.
    """

    @staticmethod
    @abstractmethod
    def goal_field(crossword: Crossword, coord: Coord) -> float:
        """
        Returns the goal value for the field at the given coordinate.

        Args:
        crossword: A Crossword object.
        coord: A Coord object.

        Returns:
        The goal value for the field at the given coordinate.
        """

    @staticmethod
    @abstractmethod
    def goal_word(word: Word) -> float:
        """
        Returns the goal value for the given word. This will be added to the field goal before approximation.
        """

    @staticmethod
    @abstractmethod
    def goal_colrow(colrow: ColRow) -> float:
        """
        Returns the goal value for the given colrow. This will be added to the field goal before approximation.
        """

    def __init__(self, crossword: Crossword) -> None:
        """
        Initializes a LocalGoalCruciverbalistBase object.
        """
        self.crossword = crossword
        self.get_raw_cache: dict[Coord, float] = {}

    def raw_get(self, coord: Coord) -> float:
        """
        Returns the raw value for the field at the given coordinate.
        This is the sum of the goal field, goal word and goal colrow.

        Args:
        coord: tuple[int, int]

        Returns:
        The raw value for the field at the given coordinate.
        """
        words = (
            Word.from_crossword(self.crossword, i)
            for i in self.crossword.get_words(coord)
        )
        column, row = ColRow.from_coord(self.crossword, coord)
        if coord not in self.get_raw_cache:
            self.get_raw_cache[coord] = (
                self.goal_field(self.crossword, coord)
                + sum(self.goal_word(w) for w in words)
                + self.goal_colrow(column)
                + self.goal_colrow(row)
            )
        return self.get_raw_cache[coord]

    def get_goal_field(self, coord: Coord) -> float:
        """
        Returns the goal value for the field at the given coordinate.

        Args:
        coord: tuple[int, int]

        Returns:
        The goal value for the field at the given coordinate.
        """
        neighbour_rows = range(
            max(0, coord[-1] - 1), min(self.crossword.max[-1], coord[-1] + 1) + 1
        )
        neighbour_cols = range(
            max(0, coord[0] - 1), min(self.crossword.max[0], coord[0] + 1) + 1
        )
        return (
            avg(
                self.raw_get((col, row))  # type: ignore
                for col in neighbour_cols
                for row in neighbour_rows
            )
            + random.random()
        )

    def get_goal_word(self, word: str) -> float:
        """
        Returns the goal value for the given word.

        Args:
        word: A string representing a word.

        Returns:
        The goal value for the given word.
        """
        return sum(self.get_goal_field(i) for i in self.crossword.words[word])

    def get_goal_colrow(self, colrow: ColRow) -> float:
        """
        Returns the goal value for the given colrow.

        Args:
        colrow: A ColRow object.

        Returns:
        The goal value for the given colrow.
        """

        return sum(self.get_goal_field(i) for i in colrow.get_coords())

    def get_goal_crossword(self) -> float:
        """
        Returns the goal value for the whole crossword.
        """
        return sum(self.get_goal_field(i) for i in self.crossword.letters.keys())

    def iter_words(self) -> Iterator[Word]:
        """
        Iterates over all words in the crossword starting with the worst ones.
        """
        words = [
            Word.from_crossword(self.crossword, word) for word in self.crossword.words
        ]
        yield from sorted(words, key=self.goal_word)

    def iter_colrows(self) -> Iterator[ColRow]:
        """
        Iterates over all colrows in the crossword starting with the worst ones.
        """
        yield from sorted(ColRow.iter(self.crossword), key=self.goal_colrow)
