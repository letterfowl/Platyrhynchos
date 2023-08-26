from functools import reduce
from .improvable import CrosswordImprovable
from .colrow import ColRow
from ..commons.misc import Coord
from ..commons.exceptions import UninsertableException

class NoConflictCrossword(CrosswordImprovable):

    def check_for_conflicts(self, coord: Coord, excluded: set[Coord]) -> bool:
        """
        Check if a coordinate has any conflicts.
        """
        neighbourhood = self.get_neighbourhood_neumann(coord)
        return any((i not in excluded and i in self.letters) for i in neighbourhood)

    def check_for_conflicts_all(self, word_letters: dict[Coord, str], excluded: set[Coord]) -> bool:
        """
        Check if a word has any conflicts.
        """
        return any(
            self.check_for_conflicts(coord, excluded=excluded)
            for coord in word_letters
        )

    def get_offset_coord_in_colrow(self, coord: Coord, colrow: ColRow, offset: int) -> Coord:
        coord_x, coord_y = coord
        return Coord((coord_x, coord_y+offset)) if colrow.is_column else Coord((coord_x+offset, coord_y))

    def get_future_word_coords(self, word: str, colrow: ColRow):
        coords = super().get_future_word_coords(word, colrow)

        excluded = self.get_near_fields(colrow)
        if self.check_for_conflicts_all(coords, excluded):
            raise UninsertableException(
                f"Word {word} cannot be inserted because of unreal intersections."
            )

        last_coord = max(coords, key=lambda x: x[0]*x[-1])
        first_coord = min(coords, key=lambda x: x[0]*x[-1])
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

    def get_near_fields(self, colrow: ColRow) -> set[Coord]:
        words_coords = reduce(
            lambda x, y: x|y[-1],
            colrow.cross_words(),
            set()
        )
        # neighbour_colrows = colrow.offset(1).get_coords()) | set(colrow.offset(-1)
        return words_coords