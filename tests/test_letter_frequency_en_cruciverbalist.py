import pytest
from platyrhynchos.cruciverbalist.letter_frequency_en import LetterFreqEnCruciverbalist
from platyrhynchos.crossword.improvable import CrosswordImprovable
from platyrhynchos.commons.misc import Coord
from platyrhynchos.crossword.colrow import ColRow
from platyrhynchos.crossword.word import Word

@pytest.fixture
def crossword1():
    return CrosswordImprovable(
        {(0, 1): "e", (1, 1): "x", (1, 2): "t", (3, 3): "a", (2, 3): "b", (7, 3): " "},
        10,
        10,
        words_horizontal={"ext": {(1, 1), (1, 2), (1, 3)}},
        crossings={(0, 1)},
    )


class TestLetterFrequencyEnCruciverbalist:
    def test_letter_frequency_en_cruciverbalist_goal_colrow(self, crossword1: CrosswordImprovable):
        lfe = LetterFreqEnCruciverbalist()
        colrow = next(crossword1.iter_colrows())
        assert lfe.goal_colrow(colrow) == 0


    def test_letter_frequency_en_cruciverbalist_goal_word(self, crossword1: CrosswordImprovable):
        lfe = LetterFreqEnCruciverbalist()
        word = Word.from_crossword(crossword1, "ext")
        assert lfe.goal_word(word) == pytest.approx(0.3, abs=0.04)


    def test_letter_frequency_en_cruciverbalist_goal_field(self, crossword1: CrosswordImprovable):
        lfe = LetterFreqEnCruciverbalist()
        coord = Coord((0, 0))
        assert lfe.goal_field(crossword1, coord) == 0

        coord = Coord((0, 1))
        assert lfe.goal_field(crossword1, coord) == pytest.approx(1/28)