import asyncio, bisect
from copy import deepcopy
from typing import Generic, TypeVar, Coroutine, Any

from ..commons.logger import logger
from ..commons.utils import random
from ..crossword import CrosswordImprovable
from ..cruciverbalist import Cruciverbalist, CruciverbalistBase
from ..crossword.colrow import ColRow

T = TypeVar("T")

cruciverbalist: CruciverbalistBase = Cruciverbalist()


def goal_function(crossword: CrosswordImprovable, turn: int) -> float:
    return len(crossword.crossings) / crossword.size


def qualifies_for_goal(crossword: CrosswordImprovable, turn: int) -> bool:
    MINIMUM_QUALIFICATION = 0.5
    return goal_function(crossword, turn) > MINIMUM_QUALIFICATION
    # return turn > 100


class HallOfFame(Generic[T]):
    def __init__(self, n: int):
        self.n = n
        self.solutions: list[tuple[float, T]] = []

    def add(self, score: float, solution: T):
        bisect.insort(self.solutions, (score, solution), key=lambda x: x[0])
        self.solutions = self.solutions[: self.n]

    def get_best(self) -> list[T]:
        return [solution for _, solution in self.solutions]

    def get_scores(self) -> list[float]:
        return [score for score, _ in self.solutions]

    def __iter__(self):
        return self.get_best()

    def non_empty(self):
        return bool(self.solutions)


async def calc_usefulness(
    colrow_prios: dict[ColRow, int], word: str, colrow: ColRow
) -> float:
    colrow_prio = colrow_prios[colrow]
    return cruciverbalist.eval_word(word, colrow) + colrow_prio


async def best_of(
    find_word_tasks: list[Coroutine[Any, Any, list[tuple[str, ColRow]]]], colrow_prios
):
    ranking: HallOfFame[tuple[str, ColRow]] = HallOfFame(10)
    for result in asyncio.as_completed(find_word_tasks):
        for word, colrow in await result:
            if word is None:
                continue
            ranking.add(
                await calc_usefulness(colrow_prios, word, colrow), (word, colrow)
            )
    if ranking.non_empty():
        logger.debug("Found words: {}", ranking.get_best())
        word, colrow = random.choices(ranking.get_best(), weights=ranking.get_scores())[
            0
        ]
        return word, colrow
    else:
        logger.info("No words found")
        return None, None


async def find_for_addition(
    crossword: CrosswordImprovable,
) -> tuple[str, ColRow] | tuple[None, None]:
    """Finds a word. Returns None if no word was found."""
    colrow_prios = {
        c: e for e, c in enumerate(cruciverbalist.choose_colrows(crossword))
    }
    find_word_tasks = [
        cruciverbalist.find_words(colrow)
        for colrow in cruciverbalist.choose_colrows(crossword)
    ]
    return await best_of(find_word_tasks, colrow_prios)


async def find_for_removal(
    crossword: CrosswordImprovable,
) -> tuple[str, ColRow] | tuple[None, None]:
    """Finds a word. Returns None if no word was found."""
    colrow_prios = {
        c: e for e, c in enumerate(list(cruciverbalist.choose_colrows(crossword))[::-1])
    }
    find_word_tasks = [
        cruciverbalist.find_removable_words(colrow)
        for colrow in cruciverbalist.choose_colrows(crossword)
    ]
    return await best_of(find_word_tasks, colrow_prios)


async def generate_crossword(
    width: int, height: int, word_amount: int
) -> CrosswordImprovable:
    logger.info(
        "I'm starting crossword generation. Requested size is {}x{} with {} words",
        width,
        height,
        word_amount,
    )
    start_word = await cruciverbalist.start_word(min(width, height))
    logger.info("Found word: {}", start_word)
    crossword = CrosswordImprovable.make(start_word, width, height)
    # logger.debug("Crossword:\n"+str(crossword))
    logger.info("I found a start word: {}", start_word)

    turn = 0
    while not qualifies_for_goal(crossword, (turn := turn+1)) and len(crossword.words) < word_amount:
        (addition_word, addition_colrow), (removal_word, _) = await asyncio.gather(find_for_addition(crossword), find_for_removal(crossword))
        if addition_word is None or addition_colrow is None:
            if removal_word is None:
                logger.error("No more words found, I'm terminating at {} words", len(crossword.words))
                break
            crossword.remove(removal_word)
        elif removal_word is None:
            crossword.add(addition_word, addition_colrow)
        else:
            removal_test = deepcopy(crossword)
            removal_test.remove(removal_word)
            addition_test = crossword
            addition_test.add(addition_word, addition_colrow)
            if goal_function(removal_test, turn) > goal_function(addition_test, turn):
                crossword = removal_test
            else:
                crossword = addition_test
    return crossword
