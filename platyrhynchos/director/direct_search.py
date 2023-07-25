from ..commons.logger import logger
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

    while len(crossword.words) < word_amount:
        word, colrow = await cruciverbalist.choose_and_fill(crossword)
        if word is None:
            logger.error("No more words found, I'm terminating at {} words", len(crossword.words))
            break
        logger.info("I'm adding {} to {}", word, colrow)
        crossword.add(word, colrow)  # type: ignore
        logger.debug("Crossword:\n" + str(crossword))
    else:
        logger.success("I finished generating the crossword with requested specifications.")
    return crossword
