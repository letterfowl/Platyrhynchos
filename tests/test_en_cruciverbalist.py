import pytest

from platyrhynchos import CrosswordImprovable
from platyrhynchos.libs.cruciverbalists.en_simple import EnglishSimpleCruciverbalist, DB_CURSOR

CRUCIVERBALIST = EnglishSimpleCruciverbalist()

@pytest.fixture
def crossword1():
    return CrosswordImprovable({(0,1):'e', (1,1):'x'}, 10, 10, words_horizontal={}, crossings = {(0,1)})


class TestDB:
    
    def runner(self, sql):
        return DB_CURSOR.execute(sql).fetchall()
    
    def test_select_words(self):
        assert len(self.runner(
            "select answer from clues limit 10"
        )) == 10
        
    def test_regex(self):
        assert self.runner(
            "select 'c' regexp '[abc]'"
        ) == [(1,)]
        
    def test_select_by_regex(self):
        no_regex = self.runner("select answer from clues where substr(answer,1,1)='A'")
        regex = self.runner(r"""
                            select answer from clues inner join 
                            (
                                select rowid as row_answer, answer regexp '^A.*' as found from clues
                                where answer is not null
                            ) 
                            on rowid=row_answer where found=1""")
        assert set(no_regex) == set(regex)

def test_findword_1st_column(crossword1):
    CRUCIVERBALIST.find_word(crossword1.colrow(1, False))