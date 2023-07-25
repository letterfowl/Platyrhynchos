from ..commons.logger import logger
from ..commons.utils import random
from ..crossword import CrosswordImprovable
from ..cruciverbalist import Cruciverbalist, CruciverbalistBase
from ..crossword.colrow import ColRow

cruciverbalist: CruciverbalistBase = Cruciverbalist()

def removal(crossword: CrosswordImprovable, colrows: list[ColRow]) -> tuple[bool, CrosswordImprovable]:
    colrow = random.choice(colrows[:len(colrows)//2])
    logger.info("I'm removing a word from {}", colrow)
    words = list(colrow.cross_words())
    if words:
        word, _ = random.choice(words)
        logger.info("I'm removing {}", word)
        new = crossword.remove(word)
        return new is not None, new if new is not None else crossword
    else:
        return False, crossword

async def generate_crossword(width: int, height: int, word_amount: int) -> CrosswordImprovable:
    logger.info("I'm starting crossword generation. Requested size is {}x{} with {} words", width, height, word_amount)
    start_word = await cruciverbalist.start_word(min(width, height))
    logger.info("Found word: {}", start_word)
    crossword = CrosswordImprovable.make(start_word, width, height)
    # logger.debug("Crossword:\n"+str(crossword))
    logger.info("I found a start word: {}", start_word)

    turn = 0
    while len(crossword.words) < word_amount:
        colrows = list(cruciverbalist.choose_colrows(crossword))
        if len(colrows) == 0:
            logger.error("No more colrows found, I'm terminating at {} words", len(crossword.words))
            break
        else:
            best_colrow_qual = cruciverbalist.eval_colrow(colrows[0])
            worst_colrow_qual = cruciverbalist.eval_colrow(colrows[-1])
            remove_chance = (best_colrow_qual-worst_colrow_qual)/(best_colrow_qual+worst_colrow_qual+turn)
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
            word, _ = random.choices(words, weights=[words[::-1].index(i)+1 for i in words])[0]
            logger.info("I'm adding {} to {} at {} words", word, colrow, len(crossword.words))
            crossword.add(word, colrow)  # type: ignore
        else:
            logger.info("No more words found, performing removal at {} words", len(crossword.words))
            for i in range(10):
                done, crossword = removal(crossword, colrows)
                if done:
                    break
            else:
                logger.error("Couldn't remove, I'm terminating at {} words", len(crossword.words))
                break
        turn += 1
    else:
        logger.success("I finished generating the crossword with requested specifications.")
    return crossword
