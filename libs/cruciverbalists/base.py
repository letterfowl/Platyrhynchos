from abc import ABC, abstractmethod
from libs.colrow import ColRow
from libs.crossword_improvable import CrosswordImprovable
from libs.utils import IsColumn

class Cruciverbalist(ABC):

    @classmethod
    def choose(cls, name: str):
        return {c.__name__:c for c in cls.__subclasses__()}.get(name)

    @abstractmethod
    def eval_colrow(self, colrow: ColRow) -> int:
        return

    def choose_colrow(self, crossword: CrosswordImprovable) -> ColRow:
        col_rows = crossword.iter_colrows()
        return max(col_rows, key=self.eval_colrow)
    
    @abstractmethod
    def select_by_regex(self, regexes: list[str]) -> list[str]:
        return
    
    @abstractmethod
    def eval_word(self, word: str, colrow: ColRow) -> int:
        return
    
    def find_word(self, colrow: ColRow) -> str:
        words = self.select_by_regex(list(colrow.yield_regexes()))
        return max(words, key=lambda word: self.eval_word(word, colrow))