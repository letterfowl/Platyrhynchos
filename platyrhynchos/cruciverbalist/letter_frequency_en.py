"""Contains a class for calculating letter frequency in English words for use in crossword puzzles."""
from ..commons.misc import Coord
from ..crossword.base import Crossword
from ..crossword.colrow import ColRow
from ..crossword.word import Word
from .exclusive_word_base import ExclusiveWordBaseCruciverbalist
from .local_goal import LocalGoalCruciverbalistBase

LETTER_FREQ_EN = list("ETAONIHSRLDUCMWYFGPBVKJXQZ")


class LetterFreqEnCruciverbalist(LocalGoalCruciverbalistBase, ExclusiveWordBaseCruciverbalist):
    """A class for calculating letter frequency in English words for use in crossword puzzles.

    This class inherits from LocalGoalCruciverbalistBase and ExclusiveWordBaseCruciverbalist.
    """

    @property
    def DB_FILE(self) -> str:
        return "en_simple.db"

    @staticmethod
    def goal_colrow(colrow: ColRow) -> float:
        """Calculate the goal value for a given ColRow object.

        Args:
            colrow (ColRow): The ColRow object to calculate the goal value for.

        Returns:
            float: The calculated goal value.
        """
        return (
            sum(i is not None for i in colrow.get()) / colrow.length + len(list(colrow.cross_words()))
        )

    @staticmethod
    def goal_word(word: Word) -> float:
        """Calculate the goal value for a given Word object.

        Args:
            word (Word): The Word object to calculate the goal value for.

        Returns:
            float: The calculated goal value.
        """
        return len(list(word.cross_words())) / len(word.word)

    @staticmethod
    def goal_field(crossword: Crossword, coord: Coord):
        """Calculate the goal value for a given crossword and coordinate.

        Args:
            crossword (Crossword): The Crossword object to calculate the goal value for.
            coord (Coord): The coordinate to calculate the goal value for.

        Returns:
            float: The calculated goal value.
        """
        letter = crossword.letters.get(coord, " ").upper()
        return (LETTER_FREQ_EN.index(letter) if letter in LETTER_FREQ_EN else len(LETTER_FREQ_EN)) / (len(LETTER_FREQ_EN) + 1)
