"""
    Simulated annealing crossword generation based on local goals
"""
import asyncio
from dataclasses import dataclass
from typing import Iterable, Type, Callable
from ..cruciverbalist.letter_frequency_en import LetterFreqEnCruciverbalist
from ..crossword.base import Crossword
from ..crossword.improvable import CrosswordImprovable
from ..crossword.colrow import ColRow
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
    """
    A class that performs a simulated annealing search to find a solution to a crossword puzzle.

    Attributes:
    - is_finished: a callable that takes a Crossword object and returns a boolean indicating whether the search is finished
    - cruciverbalist: a type of Cruciverbalist to use for generating words
    - start_temperature: the starting temperature for the simulated annealing search
    - alpha: the cooling factor for the simulated annealing search
    """

    is_finished: Callable[[Crossword], bool]
    cruciverbalist: Type[LetterFreqEnCruciverbalist] = LetterFreqEnCruciverbalist
    start_temperature: float = 1
    alpha: float = 0.9

    async def _init_crossword(
        self, width: int, height: int
    ) -> tuple[CrosswordImprovable, WordHistory]:
        """
        Initializes a crossword puzzle with a start word and returns the crossword and its history.

        Args:
        - width: the width of the crossword puzzle
        - height: the height of the crossword puzzle

        Returns:
        A tuple containing the initialized crossword puzzle and its history.
        """
        start_word = await self.cruciverbalist().start_word(max_size=min(width, height))
        logger.info("Found a start  word: {}", start_word)
        crossword = CrosswordImprovable.make(start_word, width, height)
        history: WordHistory = {i.history_id(): set() for i in crossword.iter_colrows()}  # type: ignore
        history[(False, 0)].add(start_word)  # type: ignore
        logger.info("I added the start word: {}", start_word)
        return crossword, history

    async def _disjoint_add_words(
        self, colrow: ColRow, colrow_history: set[str]
    ) -> list[CrosswordImprovable]:
        """
        Adds words to a ColRow object that do not intersect with any existing words in the ColRow.

        Args:
        - colrow: the ColRow object to add words to
        - colrow_history: the history of words already added to the ColRow

        Returns:
        A list of CrosswordImprovable objects with the added words.
        """
        words = await self.cruciverbalist(colrow.crossword).select_by_regex(
            colrow.yield_regexes(), colrow_history
        )

        crosswords = []
        for word in words:
            crossword: CrosswordImprovable = colrow.crossword.copy()  # type: ignore
            crossword.add(word, colrow.history_id())
            crosswords.append(crossword)
        return crosswords

    async def _find_word_for_field(
        self, crossword: CrosswordImprovable, field: Coord, history: WordHistory
    ) -> CrosswordImprovable | None:
        """
        Finds a word to add to a given field in the crossword puzzle.

        Args:
        - crossword: the crossword puzzle to add the word to
        - field: the field to add the word to
        - history: the history of words already added to the crossword puzzle

        Returns:
        A CrosswordImprovable object with the added word, or None if no word can be added.
        """
        column, row = ColRow.from_coord(crossword, field)
        history_column = history[column.history_id()]
        history_row = history[row.history_id()]

        col_proposals, row_proposals = await asyncio.gather(
            self._disjoint_add_words(column, history_column),
            self._disjoint_add_words(row, history_row),
        )
        if len(col_proposals) + len(row_proposals) == 0:
            return None
        return max(
            col_proposals + row_proposals,
            key=lambda x: self.cruciverbalist(x).get_goal_crossword(),
        )

    async def try_word_addition(
        self, find_words_tasks, current_goal: float
    ) -> CrosswordImprovable | None:
        """
        Tries to add a word to the crossword puzzle from a list of tasks that find words for fields.

        Args:
        - find_words_tasks: a list of tasks that find words for field ealuation
        - current_goal: the current solution's goal function value

        Returns:
        A CrosswordImprovable object with the added word, or None if no word can be added.
        """
        while find_words_tasks:
            result = await find_words_tasks.pop(0)
            result_goal = self.cruciverbalist(result).get_goal_crossword()
            if result is not None and result_goal >= current_goal:
                for task in find_words_tasks:
                    task.close()
                return result
        return None

    @staticmethod
    def _get_fields_to_check_for_additions(
        crossword: CrosswordImprovable,
        cruciverbalist: LetterFreqEnCruciverbalist,
        temperature: float,
    ) -> list[Coord]:
        """
        Returns a list of fields to check for word additions based on the temperature of the simulated annealing search.

        Args:
        - crossword: the crossword puzzle to check for word additions
        - cruciverbalist: the Cruciverbalist object to use for field 
        - temperature: the current temperature of the simulated annealing search

        Returns:
        A list of Coord objects representing the fields to check for word additions.
        """
        element_count = n_elements_from_len_and_temp(
            len(crossword.letters), temperature
        )
        return retrieve_elements(cruciverbalist.iter_words(), element_count)

    async def run(self, width: int, height: int) -> CrosswordImprovable:
        """
        Runs the simulated annealing search to find a solution to the crossword puzzle.

        Args:
        - width: the width of the crossword puzzle
        - height: the height of the crossword puzzle

        Returns:
        A CrosswordImprovable object representing the solution to the crossword puzzle.
        """
        temperature = self.start_temperature
        crossword, history = await self._init_crossword(width, height)

        while not self.is_finished(crossword):
            temperature *= self.alpha
            cruciverbalist = self.cruciverbalist(crossword)

            fields = self._get_fields_to_check_for_additions(
                crossword, cruciverbalist, temperature
            )
            find_words_tasks = [
                self._find_word_for_field(crossword, i, history) for i in fields
            ]
            result = await self.try_word_addition(
                find_words_tasks, cruciverbalist.get_goal_crossword()
            )
            if result is not None:
                crossword = result
            else:
                word_to_remove = next(cruciverbalist.iter_words(), None)
                if word_to_remove is None:
                    logger.error(
                        "No more words found, I'm terminating at {} words",
                        len(crossword.words),
                    )
                    break
                crossword.remove(word_to_remove.word)
        return crossword
