import asyncio, bisect
from typing import Generic, TypeVar

from ..commons.logger import logger
from ..commons.utils import random
from ..crossword import CrosswordImprovable
from ..cruciverbalist import Cruciverbalist, CruciverbalistBase
from ..crossword.colrow import ColRow

T = TypeVar("T")

cruciverbalist: CruciverbalistBase = Cruciverbalist()

def goal_function(crossword: CrosswordImprovable) -> float:
    return 1

def qualifies_for_goal(crossword: CrosswordImprovable) -> bool:
    MINIMUM_QUALIFICATION = 0.5
    return goal_function(crossword) > MINIMUM_QUALIFICATION

class HallOfFame(Generic[T]):
    def __init__(self, n: int):
        self.n = n
        self.solutions: list[tuple[float, T]] = []

    def add(self, score: float, solution: T):
        bisect.insort(self.solutions, (score, solution))
        self.solutions = self.solutions[:self.n]

    def get_best(self) -> list[T]:
        return [solution for _, solution in self.solutions]
    
    def get_scores(self) -> list[float]:
        return [score for score, _ in self.solutions]

    def __iter__(self):
        return self.get_best()

    def non_empty(self):
        return bool(self.solutions)

async def calc_usefulness(colrow_prios: dict[ColRow, int], word: str, colrow: ColRow) -> float:
    colrow_prio = colrow_prios[colrow]
    return cruciverbalist.eval_word(word, colrow) + colrow_prio

async def find_for_addition(
    crossword: CrosswordImprovable,
) -> tuple[str, ColRow] | tuple[None, None]:
    """Finds a word. Returns None if no word was found."""
    colrow_prios = {c: e for e, c in enumerate(cruciverbalist.choose_colrows(crossword))}
    find_word_tasks = [
        cruciverbalist.find_words(colrow)
        for colrow in cruciverbalist.choose_colrows(crossword)
    ]
    ranking = HallOfFame(10)
    for result in asyncio.as_completed(find_word_tasks):
        for word, colrow in await result:
            if word is None:
                continue
            ranking.add(await calc_usefulness(colrow_prios, word, colrow),
                        (word, colrow))
    if ranking.non_empty():
        logger.debug("Found words: {}", ranking.get_best())
        word, colrow = random.choices(
            ranking.get_best(), 
            weights=ranking.get_scores()
        )[0]
        logger.info("Chose to add {} to {}", word, colrow)
        
    else:
        logger.info("No words found")
        return None, None

async def find_for_removal(crossword: CrosswordImprovable) -> tuple[str, ColRow] | tuple[None, None]:
    """Finds a word. Returns None if no word was found."""
    colrow_prios = {c: e for e, c in enumerate(cruciverbalist.choose_colrows(crossword))}
    find_word_tasks = [
        cruciverbalist.find_words(colrow)
        for colrow in cruciverbalist.choose_colrows(crossword)
    ]
    ranking = HallOfFame(10)
    raise NotImplementedError


async def generate_crossword(
    width: int, height: int, word_amount: int
) -> CrosswordImprovable:
    logger.info(
        "I'm starting crossword generation. Requested size is {}x{} with {} words",
        width,
        height,
        word_amount,
    )
    raise NotImplementedError
    start_word = await cruciverbalist.start_word(min(width, height))
    logger.info("Found word: {}", start_word)
    crossword = CrosswordImprovable.make(start_word, width, height)
    # logger.debug("Crossword:\n"+str(crossword))
    logger.info("I found a start word: {}", start_word)

    turn = 0
    while qualifies_for_goal(crossword) and len(crossword.words) < word_amount:
        colrows = list(cruciverbalist.choose_colrows(crossword))
        if len(colrows) == 0:
            logger.error(
                "No more colrows found, I'm terminating at {} words",
                len(crossword.words),
            )
            break
        else:
            if random.random() < remove_chance:
                done, crossword = removal(crossword, colrows)
                if done:
                    turn += 1
                    continue

        for colrow in colrows[::-1]:
            logger.info("I'm choosing {} as the next to add", colrow)
            words = await cruciverbalist.find_words(colrow)
            if len(words) == 0:
                logger.error("No words found for {}, changing colrow", colrow)
                continue
            word, _ = random.choices(
                words, weights=[words[::-1].index(i) + 1 for i in words]
            )[0]
            logger.info(
                "I'm adding {} to {} at {} words", word, colrow, len(crossword.words)
            )
            crossword.add(word, colrow)  # type: ignore
        else:
            logger.info(
                "No more words found, performing removal at {} words",
                len(crossword.words),
            )
            for i in range(10):
                done, crossword = removal(crossword, colrows)
                if done:
                    break
            else:
                logger.error(
                    "Couldn't remove, I'm terminating at {} words", len(crossword.words)
                )
                break
        turn += 1
    else:
        logger.success(
            "I finished generating the crossword with requested specifications."
        )
    return crossword
