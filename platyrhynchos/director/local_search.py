import asyncio
from typing import Coroutine, Any

from ..commons.logger import logger
from ..commons.utils import random
from ..commons.misc import HallOfFame
from ..crossword import CrosswordImprovable
from ..cruciverbalist import Cruciverbalist, CruciverbalistOldBase
from ..crossword.colrow import ColRow

cruciverbalist: CruciverbalistOldBase = Cruciverbalist()


def goal_function(crossword: CrosswordImprovable, turn: int) -> float:
    return len(crossword.crossings) / crossword.size


def qualifies_for_goal(crossword: CrosswordImprovable, turn: int) -> bool:
    MINIMUM_QUALIFICATION = 0.4
    return goal_function(crossword, turn) > MINIMUM_QUALIFICATION
    # return turn > 100


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
    crossword: CrosswordImprovable, history: dict[tuple[bool, int], set[str]]
) -> tuple[str, ColRow] | tuple[None, None]:
    """Finds a word. Returns None if no word was found."""
    colrow_prios = {
        c: e for e, c in enumerate(cruciverbalist.choose_colrows(crossword))
    }
    find_word_tasks = [
        cruciverbalist.find_words(colrow, history[colrow.history_id()])
        for colrow in cruciverbalist.choose_colrows(crossword)
    ]
    return await best_of(find_word_tasks, colrow_prios)


async def find_for_removal(
    crossword: CrosswordImprovable,
) -> tuple[str, ColRow] | tuple[None, None]:
    """Finds a word that can be removed from a ColRow in a crossword. Returns `(None, None)` if no word was found."""
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
    logger.info("Found a start  word: {}", start_word)
    crossword = CrosswordImprovable.make(start_word, width, height)
    history = {i.history_id():set() for i in crossword.iter_colrows()}
    history[(False, 0)].add(start_word)
    logger.info("I added the start word: {}", start_word)

    turn = 0
    while not qualifies_for_goal(crossword, (turn := turn+1)) or len(crossword.words) < word_amount:
        (addition_word, addition_colrow), (removal_word, _) = await asyncio.gather(find_for_addition(crossword, history), find_for_removal(crossword))
        if addition_word is None or addition_colrow is None:
            if removal_word is None:
                logger.error("No more words found, I'm terminating at {} words", len(crossword.words))
                break
            crossword.remove(removal_word)
        elif removal_word is None:
            logger.info("I'm adding the word '{}' to {}", addition_word, addition_colrow)
            crossword.add(addition_word, addition_colrow)
            history[addition_colrow.history_id()].add(addition_word)
        else:
            logger.debug("I found both a word to add and a word to remove; I'm comparing them.")
            removal_test = crossword.copy()
            removal_test.remove(removal_word)
            addition_test = crossword
            addition_test.add(addition_word, addition_colrow)
            if goal_function(removal_test, turn) > goal_function(addition_test, turn):
                logger.info("I'm removing the word '{}'", removal_word)
                crossword = removal_test
            else:
                logger.info("I'm adding the word '{}' to {}", addition_word, addition_colrow)
                crossword = addition_test
                history[addition_colrow.history_id()].add(addition_word)
        for i in history.values():
            logger.warning(", ".join(i))
    return crossword
