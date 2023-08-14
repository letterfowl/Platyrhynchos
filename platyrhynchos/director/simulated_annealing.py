import random
from dataclasses import dataclass
from typing import Iterable, Type, Callable
from ..cruciverbalist.letter_frequency_en import LetterFreqEnCruciverbalist
from ..crossword.base import Crossword
from ..crossword.improvable import CrosswordImprovable
from ..crossword.colrow import ColRow
from ..commons.utils import random
from ..commons.misc import Coord, WordHistory
from ..commons.logger import logger
from math import ceil as ceiling

def retrieve_elements(iterable: Iterable, n_elements: int) -> list:
    """Returns the first n elements of an iterable"""
    return [i for i, _ in zip(iterable, range(n_elements))]

def n_elements_from_len_and_temp(length: int, temperature: float) -> int:
    """Returns the number of elements to retrieve from a list of given length and a given temperature"""
    return ceiling(length * (1 - temperature))

@dataclass
class SimulatedAnnealingCrosswordSearch:
    is_finished: Callable[[Crossword], bool]
    cruciverbalist: Type[LetterFreqEnCruciverbalist] = LetterFreqEnCruciverbalist
    temperature: float = 1
    alpha: float = 0.9

    async def _init_crossword(self, width: int, height: int) -> tuple[CrosswordImprovable, WordHistory]:
        start_word = await self.cruciverbalist().start_word(max_size=min(width, height))
        logger.info("Found a start  word: {}", start_word)
        crossword = CrosswordImprovable.make(start_word, width, height)
        history: WordHistory = {i.history_id():set() for i in crossword.iter_colrows()} # type: ignore
        history[(False, 0)].add(start_word) # type: ignore
        logger.info("I added the start word: {}", start_word)
        return crossword, history
        

    async def run(self, width: int, height: int) -> CrosswordImprovable:
        crossword, history = await self._init_crossword(width, height)
        
        while not self.is_finished(crossword):
            self.temperature *= self.alpha
            cruciverbalist = self.cruciverbalist(crossword)

            element_num = n_elements_from_len_and_temp(len(crossword.letters), self.temperature)
            fields = retrieve_elements(cruciverbalist.iter_words(), element_num)
            # TODO: field iter should be async
            for field in fields:
                column, row = ColRow.from_coord(crossword, field)
                # TODO: add retrieve code
                break
            else:
                word_to_remove = next(cruciverbalist.iter_words(), None)
                if word_to_remove is None:
                    logger.error("No more words found, I'm terminating at {} words", len(crossword.words))
                    break
                crossword.remove(word_to_remove.word)
