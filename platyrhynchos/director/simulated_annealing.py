from ..commons.logger import logger
from ..commons.utils import random
from ..crossword import CrosswordImprovable
from ..cruciverbalist import Cruciverbalist, CruciverbalistBase

cruciverbalist: CruciverbalistBase = Cruciverbalist()


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

        if len(colrows) == 1:
            colrow = colrows[0]
        else:
            best_colrow_qual = cruciverbalist.eval_colrow(colrows[0])
            worst_colrow_qual = cruciverbalist.eval_colrow(colrows[-1])
            remove_chance = (best_colrow_qual-worst_colrow_qual)/(best_colrow_qual+worst_colrow_qual+turn)
            if random.random() < remove_chance:
                colrow = random.choice(colrows[:len(colrows)//2])
                logger.info("I'm removing a word from {}", colrow)
                words = list(colrow.cross_words())
                if words:
                    word, _ = random.choice(words)
                    logger.info("I'm removing {}", word)
                    crossword.remove(word)
                    turn += 1
                    continue

            colrow = random.choice(colrows[len(colrows)//2:])

        logger.info("I'm choosing {} as the next to add", colrow)
        words = await cruciverbalist.find_words(colrow)
        if len(words) == 0:
            logger.error("No more words found, I'm terminating at {} words", len(crossword.words))
            break
        word, _ = random.choices(words, weights=[words[::-1].index(i) for i in words])
        logger.info("I'm adding {} to {}", word, colrow)
        crossword.add(word, colrow)  # type: ignore
        turn += 1

    else:
        logger.success("I finished generating the crossword with requested specifications.")
    return crossword
