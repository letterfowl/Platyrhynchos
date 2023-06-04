from ..cruciverbalist import Cruciverbalist, CruciverbalistBase
from ..crossword import CrosswordImprovable
from ..commons.logger import logger

cruciverbalist: CruciverbalistBase = Cruciverbalist()

async def generate_crossword(width: int, height: int, word_amount: int) -> str:
    logger.info("I'm starting crossword generation. Requested size is {}x{} with {} words", width, height, word_amount)
    start_word = await cruciverbalist.start_word()
    crossword = CrosswordImprovable.make(start_word, width, height)
    logger.debug("Crossword:\n"+str(crossword))
    logger.info("I found a start word: {}", start_word)

    while len(crossword.words) < word_amount:
        to_add = await cruciverbalist.choose_and_fill(crossword)
        if to_add[0] is None:
            logger.error("No more words found, I'm terminating at {} words", len(crossword.words))
            break
        logger.info("I'm adding {} to {}", *to_add)
        crossword.add(*to_add)  # type: ignore
        logger.debug("Crossword:\n"+str(crossword))
    else:
        logger.success("I finished generating the crossword with requested specifications.")
    return crossword