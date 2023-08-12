from .local_goal import LocalGoalCruciverbalistBase
from .exclusive_word_base import ExclusiveWordBaseCruciverbalist
from ..crossword.colrow import ColRow
from ..crossword.word import Word
from ..crossword.base import Crossword
from ..commons.misc import Coord

LETTER_FREQ_EN = list("ETAONIHSRLDUCMWYFGPBVKJXQZ"[::-1])

class LetterFreqEnSimpleCruciverbalist(LocalGoalCruciverbalistBase, ExclusiveWordBaseCruciverbalist):

    @staticmethod
    def goal_colrow(colrow: ColRow) -> float:
        return 1 / (sum(i is not None for i in colrow.get()) + 1)

    @staticmethod
    def goal_word(word: Word) -> float:
        return len(list(word.cross_words())) / len(word.word)

    @staticmethod
    def goal_field(crossword: Crossword, coord: Coord):
        letter = crossword.letters.get(coord, None)
        return (LETTER_FREQ_EN.index(letter)+1 if letter in LETTER_FREQ_EN else len(LETTER_FREQ_EN)+1) / len(LETTER_FREQ_EN)+2
