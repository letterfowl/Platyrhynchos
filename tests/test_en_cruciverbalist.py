from string import ascii_uppercase

import pytest

from platyrhynchos import CrosswordImprovable
from platyrhynchos.commons.alphabit import MAX_ALPHABIT, Alphabit
from platyrhynchos.cruciverbalist.en_simple import EnglishSimpleCruciverbalist
from platyrhynchos.exclusive.cpython import cursor_execute
from platyrhynchos.commons.exceptions import DatabaseException

pytest_plugins = ("pytest_asyncio",)

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
        words_horizontal={"ext": {(1, 1), (1, 2), (1, 3)}},
        crossings={(0, 1)},
    )


@pytest.fixture
def cruciverbalist():
    return EnglishSimpleCruciverbalist()


class TestDB:
    def test_start_db(self):
        assert cursor_execute("select 1+1")[0][0] == 2

    def test_download_works(self, cruciverbalist: EnglishSimpleCruciverbalist):
        alphabit = cursor_execute("select alphabit, typeof(alphabit) from clues limit 10")
        assert len(alphabit) == 10
        assert all(i[0] is not None and len(i[0]) == 26 and i[1].lower() == "bit" for i in alphabit)

    def test_select_words(self, cruciverbalist: EnglishSimpleCruciverbalist):
        assert len(cursor_execute("select answer from clues limit 10")) == 10

    def test_regex(self):
        assert cursor_execute("select 'c' ~ '[abc]'") == [(1,)]

    def test_select_by_regex(self, cruciverbalist: EnglishSimpleCruciverbalist):
        no_regex = cursor_execute("select answer from clues where answer^@'A'")
        regex = cursor_execute(r"select answer from clues where regexp_matches(answer, '^A')")
        assert set(no_regex) == set(regex)

    @pytest.mark.asyncio
    async def test_select_by_regex_w_alphabit(self, cruciverbalist: EnglishSimpleCruciverbalist):
        cruciverbalist.RUN_WITH_ALPHABIT = True
        words = await cruciverbalist.select_by_regex(["^RESOR."], [], 10)
        assert "RESORT" in words
        assert "RESORTS" in words
        assert all(i.startswith("RESOR") for i in words)

    @pytest.mark.asyncio
    async def test_select_by_regex_wo_alphabit(self, cruciverbalist: EnglishSimpleCruciverbalist):
        cruciverbalist.RUN_WITH_ALPHABIT = False
        words = await cruciverbalist.select_by_regex(["^RESOR."], [], 10)
        assert "RESORT" in words
        assert "RESORTS" in words
        assert all(i.startswith("RESOR") for i in words)

    @pytest.mark.asyncio
    async def test_select_by_regex_wo_alphabit_exclude(self, cruciverbalist: EnglishSimpleCruciverbalist):
        cruciverbalist.RUN_WITH_ALPHABIT = False
        words = await cruciverbalist.select_by_regex(["^RESOR."], ["RESORT"], 10)
        assert "RESORT" not in words
        assert "RESORTS" in words
        assert all(i.startswith("RESOR") for i in words)

    @pytest.mark.asyncio
    async def test_select_random(self, cruciverbalist: EnglishSimpleCruciverbalist):
        assert isinstance(await cruciverbalist.start_word(20), str)


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

    def test_empty(self, cruciverbalist: EnglishSimpleCruciverbalist):
        word = Alphabit("").to_query()
        assert (
            len(cursor_execute(f"select answer from clues where bit_count('{word}'::BIT | alphabit)!=length(alphabit)"))
            == 0
        )

    @pytest.mark.parametrize("word", SAMPLE_WORDS)
    def test_words(self, word: str):
        alp = Alphabit(word).to_query()
        result = cursor_execute(f"select answer from clues where bit_count('{alp}'::BIT | alphabit)=length(alphabit)")
        assert (word,) in result


class TestEnSimpleFindWord:
    @pytest.mark.asyncio
    async def test_1st_column(
        self,
        crossword1: CrosswordImprovable,
        cruciverbalist: EnglishSimpleCruciverbalist,
    ):
        t, _ = await cruciverbalist.find_word(crossword1.colrow(True, 1))
        assert t[1:3] == "XT"

    @pytest.mark.asyncio
    async def test_1st_row(
        self,
        crossword1: CrosswordImprovable,
        cruciverbalist: EnglishSimpleCruciverbalist,
    ):
        t, _ = await cruciverbalist.find_word(crossword1.colrow(False, 1))
        assert t[:2] == "EX"

    @pytest.mark.asyncio
    async def test_1st_weird_row(
        self,
        crossword1: CrosswordImprovable,
        cruciverbalist: EnglishSimpleCruciverbalist,
    ):
        t, _ = await cruciverbalist.find_word(crossword1.colrow(False, 3))
        assert len(t) <= 7

class TestExclusiveWordBase:
    
    @pytest.mark.asyncio
    async def test_select_by_regex_empty(self, cruciverbalist: EnglishSimpleCruciverbalist):
        assert await cruciverbalist.select_by_regex([], []) == []

    @pytest.mark.asyncio
    async def test_start_word_empty(self, cruciverbalist: EnglishSimpleCruciverbalist):
        with pytest.raises(DatabaseException):
            cruciverbalist.start_word(0)