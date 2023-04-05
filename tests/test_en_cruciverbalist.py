from contextlib import suppress
from string import ascii_uppercase
from os import remove as remove_file

import pytest

from platyrhynchos import CrosswordImprovable
from platyrhynchos.commons.alphabit import to_alphabit, MAX_ALPHABIT
from platyrhynchos.cruciverbalists.en_simple import EnglishSimpleCruciverbalist, prepare_database
from platyrhynchos.commons.utils import app_dir

CRUCIVERBALIST = EnglishSimpleCruciverbalist()

@pytest.fixture
def crossword1():
    return CrosswordImprovable({(0,1):'e', (1,1):'x', (1,2):'t', (3,3):'a', (2,3):'b', (7,3):' '}, 10, 10, words_horizontal={}, crossings = {(0,1)})

@pytest.fixture
def runner():
    _, c = prepare_database()
    def _runner(command: str):
        return c.sql(command).fetchall()
    return _runner

class TestDB:

    def test_download(self):
        with suppress(FileNotFoundError):
            remove_file(app_dir("user_cache_dir", "en_simple.db"))
        a, _ = prepare_database()
        assert a is not None

    def test_select_words(self, runner):
        assert len(runner(
            "select answer from clues limit 10"
        )) == 10

    def test_regex(self, runner):
        assert runner(
            "select 'c' ~ '[abc]'"
        ) == [(1,)]

    def test_select_by_regex(self, runner):
        no_regex = runner("select answer from clues where answer^@'A'")
        regex = runner(r"select answer from clues where regexp_matches(answer, '^A')")
        assert set(no_regex) == set(regex)

class TestAlphabit:

    def test_single_z(self):
        assert to_alphabit('z').to01() == '1'+"0"*(len(ascii_uppercase)-1)

    def test_xyz(self):
        assert to_alphabit('xyz').to01() == '111'+"0"*(len(ascii_uppercase)-3)

    def test_xz(self):
        assert to_alphabit('xz').to01()  == '101'+"0"*(len(ascii_uppercase)-3)

    def test_max(self):
        assert to_alphabit(ascii_uppercase).to01() == '1'*len(ascii_uppercase)

    def test_imp_use(self):
        word = to_alphabit('xyz')
        query = to_alphabit('y')
        assert (~query | word) == MAX_ALPHABIT

def test_findword_1st_column(crossword1: CrosswordImprovable):
    t, _ = CRUCIVERBALIST.find_word(crossword1.colrow(True, 1))
    assert t[1:3] == "XT"

def test_findword_1st_row(crossword1: CrosswordImprovable):
    t, _ = CRUCIVERBALIST.find_word(crossword1.colrow(False, 1))
    assert t[:2] == "EX"

def test_findword_1st_weird_row(crossword1: CrosswordImprovable):
    t, _ = CRUCIVERBALIST.find_word(crossword1.colrow(False, 3))
    assert len(t)<=7