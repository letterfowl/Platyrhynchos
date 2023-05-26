from string import ascii_uppercase

import pytest

from platyrhynchos import CrosswordImprovable
from platyrhynchos.commons.alphabit import MAX_ALPHABIT, Alphabit
from platyrhynchos.cruciverbalists.en_simple import EnglishSimpleCruciverbalist, download_db
from platyrhynchos.exclusive.cpython import cursor_execute

SAMPLE_WORDS = [
    "PRECIPICE",
    "AFFABLE",
    "TIDAL",
    "EXTINCT",
    "KAPUT",
    "CAMERA",
    "HUMID",
    "A BULL IN A CHINA SHOP",
    "FUNCTIONARY",
    "RESORT",
]


@pytest.fixture
def crossword1():
    return CrosswordImprovable(
        {(0, 1): "e", (1, 1): "x", (1, 2): "t", (3, 3): "a", (2, 3): "b", (7, 3): " "},
        10,
        10,
        words_horizontal={},
        crossings={(0, 1)},
    )


@pytest.fixture
def runner():
    def _runner(command: str):
        return cursor_execute(command).fetchall()

    return _runner


@pytest.fixture
def cruciverbalist():
    return EnglishSimpleCruciverbalist()


class TestDB:
    def test_start_db(self, runner):
        assert runner("select 1+1")[0][0] == 2

    def test_download_works(self, runner):
        alphabit = runner("select alphabit, typeof(alphabit) from clues limit 10")
        assert len(alphabit) == 10
        assert all(i[0] is not None and len(i[0]) == 26 and i[1].lower() == "bit" for i in alphabit)

    def test_select_words(self, runner):
        assert len(runner("select answer from clues limit 10")) == 10

    def test_regex(self, runner):
        assert runner("select 'c' ~ '[abc]'") == [(1,)]

    def test_select_by_regex(self, runner):
        no_regex = runner("select answer from clues where answer^@'A'")
        regex = runner(r"select answer from clues where regexp_matches(answer, '^A')")
        assert set(no_regex) == set(regex)


class TestAlphabit:
    def test_single_z(self):
        assert Alphabit("z").bittarray.to01() == "1" + "0" * (len(ascii_uppercase) - 1)

    def test_xyz(self):
        assert Alphabit("xyz").bittarray.to01() == "111" + "0" * (len(ascii_uppercase) - 3)

    def test_xz(self):
        assert Alphabit("xz").bittarray.to01() == "101" + "0" * (len(ascii_uppercase) - 3)

    def test_max(self):
        assert Alphabit(ascii_uppercase).bittarray.to01() == "1" * len(ascii_uppercase)

    def test_imp_use(self):
        word = Alphabit("xyz").bittarray
        query = Alphabit("y").bittarray
        assert (~query | word) == MAX_ALPHABIT.bittarray

    def test_empty(self, runner):
        word = Alphabit("").to_query()
        assert len(runner(f"select answer from clues where bit_count({word} | alphabit)!=length(alphabit)")) == 0

    @pytest.mark.parametrize("word", SAMPLE_WORDS)
    def test_words(self, word, runner):
        alp = Alphabit(word).to_query()
        result = runner(f"select answer from clues where bit_count({alp} | alphabit)=length(alphabit)")
        assert (word,) in result


class TestFindWord:
    def test_1st_column(
        self,
        crossword1: CrosswordImprovable,
        cruciverbalist: EnglishSimpleCruciverbalist,
    ):
        t, _ = cruciverbalist.find_word(crossword1.colrow(True, 1))
        assert t[1:3] == "XT"

    def test_1st_row(
        self,
        crossword1: CrosswordImprovable,
        cruciverbalist: EnglishSimpleCruciverbalist,
    ):
        t, _ = cruciverbalist.find_word(crossword1.colrow(False, 1))
        assert t[:2] == "EX"

    def test_1st_weird_row(
        self,
        crossword1: CrosswordImprovable,
        cruciverbalist: EnglishSimpleCruciverbalist,
    ):
        t, _ = cruciverbalist.find_word(crossword1.colrow(False, 3))
        assert len(t) <= 7
