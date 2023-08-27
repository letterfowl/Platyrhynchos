from functools import reduce
from .improvable import CrosswordImprovable
from .colrow import ColRow
from ..commons.misc import ColRowId, Coord
from ..commons.exceptions import UninsertableException


class NoConflictCrossword(CrosswordImprovable):
    def check_for_conflicts(self, coord: Coord, excluded: set[Coord]) -> bool:
        """
        Check if a coordinate has any conflicts.
        """
        neighbourhood = self.get_neighbourhood_neumann(coord)
        return any((i not in excluded and i in self.letters) for i in neighbourhood)

    def check_for_conflicts_all(
        self, word_letters: dict[Coord, str], excluded: set[Coord]
    ) -> bool:
        """
        Check if a word has any conflicts.
        """
        return any(
            self.check_for_conflicts(coord, excluded=excluded) for coord in word_letters
        )

    def get_offset_coord_in_colrow(
        self, coord: Coord, colrow: ColRow, offset: int
    ) -> Coord:
        coord_x, coord_y = coord
        return (
            Coord((coord_x, coord_y + offset))
            if colrow.is_column
            else Coord((coord_x + offset, coord_y))
        )

    def get_future_word_coords(self, word: str, colrow: ColRow):
        coords = super().get_future_word_coords(word, colrow)

        excluded = self.get_cross_word_fields(colrow)
        if self.check_for_conflicts_all(coords, excluded):
            raise UninsertableException(
                f"Word {word} cannot be inserted because of unreal intersections."
            )

        last_coord = max(coords, key=lambda x: x[0] * x[-1])
        first_coord = min(coords, key=lambda x: x[0] * x[-1])
        coord_after_last = self.get_offset_coord_in_colrow(last_coord, colrow, 1)
        coord_before_first = self.get_offset_coord_in_colrow(first_coord, colrow, -1)
        if self.letters.get(coord_after_last, None) is not None:
            raise UninsertableException(
                f"Word {word} cannot be inserted because it lacks an empty field at the end."
            )
        if self.letters.get(coord_before_first, None) is not None:
            raise UninsertableException(
                f"Word {word} cannot be inserted because it lacks an empty field before the beginning."
            )

        return coords

    def get_cross_word_fields(self, colrow: ColRow) -> set[Coord]:
        """
        Returns the set of coordinates representing the fields of the words intersecting with the given colrow.

        Args:
            self: The current instance of the class.
            colrow (ColRow): The colrow to find intersecting word fields for.

        Returns:
            set[Coord]: The set of coordinates representing the fields of the cross words intersecting with the given colrow.
        """
        return reduce(lambda x, y: x | y[-1], colrow.cross_words(), set())

    def get_for_subparts(self, colrow_id: ColRowId):
        """
        Generates the argument for regex generation while separating them based on conflicts and existing words.

        Args:
            self: The current instance of the class.
            colrow_id (ColRowId): The ID of the colrow.

        Yields:
            list[str]: A segment of the colrow's subparts that do not have conflicts or overlap with existing words.
        """
        colrow = self.colrow(*colrow_id)
        colrow_values = zip(colrow.get_coords(), colrow.get())

        in_words = reduce(lambda x, y: x | y[-1], colrow.in_words(), set())

        excluded = self.get_cross_word_fields(colrow)
        segment = []
        for coord, letter in colrow_values:
            if self.check_for_conflicts(coord, excluded=excluded) or coord in in_words:
                if segment:
                    yield segment
                segment = []
            else:
                segment.append(letter)
        yield segment
