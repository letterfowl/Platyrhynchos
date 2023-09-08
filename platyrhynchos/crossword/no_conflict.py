from functools import reduce
from typing import Optional
from .improvable import CrosswordImprovable
from .colrow import ColRow
from ..commons.misc import ColRowId, Coord
from ..commons.logger import logger
from ..commons.exceptions import UninsertableException
from .word import Word


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

    def _get_possible_indexes(self, word:str, colrow: ColRow):
        for start_index in colrow.pos_of_word_iter(word):
            indexes = ((start_index + i, letter) for i, letter in enumerate(word))
            if colrow.is_column:
                yield {Coord((colrow.index, index)): letter for index, letter in indexes}
            else:
                yield {Coord((index, colrow.index)): letter for index, letter in indexes}

    def get_future_word_coords(self, word: str, colrow: ColRow):
        possible_offsets = []
        for coords in self._get_possible_indexes(word, colrow):
            excluded = self.get_cross_word_fields(colrow)
            
            # This is used to detect any intrusions into existing words (also detecting unreal intersections)
            if self.check_for_conflicts_all(coords, excluded):
                logger.debug(
                    f"Word {word} cannot be inserted into {colrow} ({min(coords, key=lambda x: x[0]*x[-1])}) because of unreal intersections."
                )
                continue

            possible_offsets.append(coords)
        if not possible_offsets:
            raise UninsertableException(
                f"Word {word} cannot be inserted into {colrow} because it lacks a possible offset."
            )
        return max(possible_offsets, key=lambda x: len(set(x) & set(self.letters)))

    def get_reserved_at_beginning_and_end(
        self,
        word: Word | str,
        coords: Optional[set[Coord]] = None,
        colrow: Optional[ColRow] = None,
    ) -> tuple[Coord, Coord]:
        if colrow is None or coords is None:
            if isinstance(word, Word):
                colrow = word.colrow
                coords = word.letter_fields
            else:
                raise ValueError("Either word object or colrow and coords must be given.")

        last_coord = max(coords, key=lambda x: (1+x[0]) * (1+x[-1]))
        first_coord = min(coords, key=lambda x: (1+x[0]) * (1+x[-1]))
        coord_after_last = self.get_offset_coord_in_colrow(last_coord, colrow, 1)
        coord_before_first = self.get_offset_coord_in_colrow(first_coord, colrow, -1)
        return (coord_after_last, coord_before_first)

    def get_reserved_fields_in_colrow(self, colrow: ColRow) -> set[Coord]:
        """
        Returns a set of coordinates representing the reserved fields in a given ColRow.

        Args:
            self: The instance of the class.
            colrow: The ColRow to find the used fields for.

        Returns:
            set[Coord]: A set of coordinates representing the used fields.
        """
        in_words = reduce(lambda x, y: x | y[-1], colrow.in_words(), set())
        for word, _ in colrow.in_words():
            in_words.update(
                self.get_reserved_at_beginning_and_end(Word.from_colrow(colrow, word))
            )
        return in_words

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

        in_words = self.get_reserved_fields_in_colrow(colrow)

        excluded = self.get_cross_word_fields(colrow)
        segment = []
        for coord, letter in colrow_values:
            if self.check_for_conflicts(coord, excluded=excluded) or coord in in_words:
                if segment:
                    yield segment
                segment = []
            else:
                segment.append(letter)
        if segment:
            yield segment