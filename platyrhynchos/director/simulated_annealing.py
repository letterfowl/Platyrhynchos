"""
    Simulated annealing crossword generation based on local goals
"""

import asyncio
import contextlib
from dataclasses import dataclass
from math import ceil as ceiling
from math import log
from typing import Callable, Iterable, Type

from typing import AsyncIterator
from ..commons.logger import logger
from ..commons.misc import ColRowId, Coord, WordHistory
from ..commons.exceptions import UninsertableException
from ..crossword.base import Crossword
from ..crossword.colrow import ColRow
from ..crossword.improvable import CrosswordImprovable
from ..cruciverbalist.letter_frequency_en import LetterFreqEnCruciverbalist
from ..crossword.no_conflict import NoConflictCrossword

BAD_WORD_THRESHOLD = 0.3
GROWTH_CUTTER = 10
GROWTH_BASE = 0.2


def retrieve_elements(iterable: Iterable, n_elements: int) -> list:
    """Returns the first n elements of an iterable"""
    return [i for i, _ in zip(iterable, range(n_elements))]


g_factor = 1.1 - 0.1 * GROWTH_BASE


def calculate_elements(turn: int):
    return ceiling(log(turn, g_factor) / GROWTH_CUTTER) + 1


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
        logger.info("Found a start word: {}", start_word)
        crossword = NoConflictCrossword.make(start_word, width, height)
        history: WordHistory = {i.history_id(): set() for i in crossword.iter_colrows()}  # type: ignore
        history[(False, 0)].add(start_word)  # type: ignore
        logger.info("I added the start word: {}", start_word)
        return crossword, history

    async def _disjoint_add_words(
        self, colrow: ColRow, colrow_history: set[str]
    ) -> AsyncIterator[tuple[CrosswordImprovable, ColRow, str]]:
        """
        Adds words to a ColRow object that do not intersect with any existing words in the ColRow.

        Args:
        - colrow: the ColRow object to add words to
        - colrow_history: the history of words already added to the ColRow

        Returns:
        A list of CrosswordImprovable objects with the added words.
        """
        TARGET_WORD_AMOUNT = 6

        words_gen = self.cruciverbalist(colrow.crossword).iter_select_by_regex(
            colrow.yield_regexes(), list(colrow_history), word_amount=TARGET_WORD_AMOUNT
        )

        found = 0
        while (words := await anext(words_gen)) and found < TARGET_WORD_AMOUNT:
            for word in words:
                logger.debug("I'm testing the addition of {}", word)
                crossword: CrosswordImprovable = colrow.crossword.copy()  # type: ignore
                try:
                    crossword.add(word, colrow.history_id())
                except UninsertableException:
                    logger.debug("I couldn't add {}", word)
                    continue
                yield crossword, colrow, word
            found += len(words)

    async def _find_word_for_field(
        self, crossword: CrosswordImprovable, field: Coord, history: WordHistory
    ):
        # sourcery skip: reintroduce-else, swap-if-else-branches, use-named-expression
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
        blocked_column = history[column.history_id()] | set(crossword.words)
        blocked_row = history[row.history_id()] | set(crossword.words)

        col_proposals = self._disjoint_add_words(column, blocked_column)
        row_proposals = self._disjoint_add_words(row, blocked_row)

        with contextlib.suppress(StopAsyncIteration):
            while True:
                yield await asyncio.gather(anext(col_proposals), anext(row_proposals))

    async def try_word_addition(
        self, find_words_tasks, current_goal: float
    ) -> tuple[CrosswordImprovable, ColRowId, str] | tuple[None, None, None]:
        """
        Tries to add a word to the crossword puzzle from a list of tasks that find words for fields.

        Args:
        - find_words_tasks: a list of tasks that find words for field ealuation
        - current_goal: the current solution's goal function value

        Returns:
        A CrosswordImprovable object with the added word, or None if no word can be added.
        """
        for task in find_words_tasks:
            async for result, colrow, word in task:
                if result is None:
                    continue
                result_goal = self.cruciverbalist(result).get_goal_crossword()
                if result_goal >= current_goal:
                    return result, colrow, word
        return None, None, None


    @staticmethod
    def _get_fields_to_check_for_additions(
        crossword: CrosswordImprovable,
        cruciverbalist: LetterFreqEnCruciverbalist,
        turn: int,
    ) -> list[Coord]:
        """
        Returns a list of fields to check for word additions based on the turn of the simulated annealing search.

        Args:
        - crossword: the crossword puzzle to check for word additions
        - cruciverbalist: the Cruciverbalist object to use for field
        - turn: the current turn

        Returns:
        A list of Coord objects representing the fields to check for word additions.
        """
        element_count = min(calculate_elements(turn), len(crossword.letters))
        return retrieve_elements(cruciverbalist.iter_fields(), element_count)

    async def run(self, width: int, height: int) -> CrosswordImprovable:
        """
        Runs the simulated annealing search to find a solution to the crossword puzzle.

        Args:
        - width: the width of the crossword puzzle
        - height: the height of the crossword puzzle

        Returns:
        A CrosswordImprovable object representing the solution to the crossword puzzle.
        """
        turn = 0
        crossword, history = await self._init_crossword(width, height)

        while not self.is_finished(crossword):
            turn += 1
            logger.info("Turn {}", turn)

            cruciverbalist = self.cruciverbalist(crossword)

            fields = self._get_fields_to_check_for_additions(
                crossword, cruciverbalist, turn
            )
            find_words_tasks = (
                self._find_word_for_field(crossword, i, history) for i in fields
            )
            result, colrow, word = await self.try_word_addition(
                find_words_tasks, cruciverbalist.get_goal_crossword()
            )
            if result is not None and word is not None and colrow is not None:
                assert word not in history[colrow.history_id()]
                logger.success(
                    "I added words to the crossword: {}",
                    "; ".join(set(result.words).difference(crossword.words)),
                )
                history[colrow.history_id()].add(word)
                crossword = result
            else:
                logger.debug("I didn't find any words to add, trying to remove")
                # worst = next(cruciverbalist.iter_words())
                # logger.debug("Worst word: {} (goal:{})", worst.word, cruciverbalist.get_goal_word(worst) / len(worst.word))
                bad_words = (
                    i
                    for i in cruciverbalist.iter_words()
                    if cruciverbalist.goal_word(i) < BAD_WORD_THRESHOLD
                )
                word_to_remove = next(bad_words, None)
                if word_to_remove is not None:
                    logger.warning("I'm removing the word {}", word_to_remove.word)
                    result = crossword.remove(word_to_remove.word)
                    if result is not None:
                        crossword = result
                        logger.success("I removed the word {}", word_to_remove.word)
                        continue
                logger.error(
                    "No more options found, I'm terminating at {} words",
                    len(crossword.words),
                )
                break

        logger.success("I'm done!")
        return crossword

    async def get_react_readable(
        self,
        crossword: CrosswordImprovable,
    ) -> dict[str, dict[int, dict[str, str | int]]]:
        """Generate a react-readable representation of the crossword puzzle.

        Args:
            crossword (CrosswordImprovable): The crossword puzzle to generate a readable representation of.

        Returns:
            dict[str, dict[int, dict[str, str | int]]]: A dictionary containing the vertical and horizontal words of the crossword puzzle,
            along with their corresponding clues, answers, and positions.
        """
        clues = await self.cruciverbalist(crossword).get_clues(list(crossword.words))
        vertical: dict[int, dict[str, str | int]] = {
            num: {
                "answer": word,
                "clue": clues[word],
                "row": min(i[1] for i in fields),
                "col": min(i[0] for i in fields),
            }
            for num, (word, fields) in enumerate(
                crossword.words_vertical.items(), start=1
            )
        }
        horizontal: dict[int, dict[str, str | int]] = {
            num: {
                "answer": word,
                "clue": clues[word],
                "row": min(i[1] for i in fields),
                "col": min(i[0] for i in fields),
            }
            for num, (word, fields) in enumerate(
                crossword.words_horizontal.items(), start=len(vertical) + 1
            )
        }
        return {
            "down": vertical,
            "across": horizontal,
        }
