from dataclasses import dataclass, field
from functools import cached_property
from ..commons.misc import Coord
from typing import TypeVar

CrosswordT = TypeVar("CrosswordT", bound="Crossword")


@dataclass(init=True, repr=True)
class Crossword:
    letters: dict[Coord, str]
    words_horizontal: dict[str, set[Coord]] = field(default_factory=dict)
    # clues_horizontal: dict[Coord, str]
    words_vertical: dict[str, set[Coord]] = field(default_factory=dict)
    # clues_vertical: dict[Coord, str] = field(default_factory=dict)
    crossings: set[Coord] = field(default_factory=set)

    @cached_property
    def words(self) -> dict[str, set[Coord]]:
        return self.words_horizontal | self.words_vertical

    @cached_property
    def max(self) -> Coord:
        max_field_v, max_field_h = zip(*self.letters.keys())
        return Coord((max(max_field_v), max(max_field_h)))

    @cached_property
    def size(self) -> int:
        # pylint: disable=unpacking-non-sequence
        size_x, size_y = self.max
        return (size_x + 1) * (size_y + 1)

    @cached_property
    def min(self) -> Coord:
        min_field_v, min_field_h = zip(*self.letters.keys())
        return Coord((min(min_field_v), min(min_field_h)))

    def relative(self: CrosswordT, rel_to: Coord) -> CrosswordT:
        delta_v, delta_h = rel_to
        return self.__class__(
            letters={
                Coord((v - delta_v, h - delta_h)): i
                for (v, h), i in self.letters.items()
            },
            words_vertical={
                word: {Coord((v - delta_v, h - delta_h)) for (v, h) in i}
                for word, i in self.words_vertical.items()
            },
            words_horizontal={
                word: {Coord((v - delta_v, h - delta_h)) for (v, h) in i}
                for word, i in self.words_horizontal.items()
            },
            crossings={Coord((v - delta_v, h - delta_h)) for (v, h) in self.crossings},
        )

    def absolute(self):
        rel_to_min = self.relative(self.min)
        assert rel_to_min.min == (0, 0), rel_to_min.min
        return rel_to_min

    def rotate(self: CrosswordT) -> CrosswordT:
        return self.__class__(
            letters={Coord((j, i)): letter for (i, j), letter in self.letters.items()},
            words_horizontal={
                word: {Coord((h, v)) for (v, h) in i}
                for word, i in self.words_vertical.items()
            },
            words_vertical={
                word: {Coord((h, v)) for (v, h) in i}
                for word, i in self.words_horizontal.items()
            },
            crossings={Coord((j, i)) for (i, j) in self.crossings},
        )
