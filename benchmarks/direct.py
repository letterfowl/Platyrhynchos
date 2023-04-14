from contextlib import suppress

from platyrhynchos.commons.logger import logger
from platyrhynchos.crossword import CrosswordImprovable
from platyrhynchos.cruciverbalists import EnglishSimpleCruciverbalist

with suppress(ModuleNotFoundError):
    import functiontrace

    functiontrace.trace()

cruciverbalist = EnglishSimpleCruciverbalist()

crossword = CrosswordImprovable.make(cruciverbalist.start_word(), 10, 10)

for _ in range(10):
    to_add = cruciverbalist.choose_and_fill(crossword)
    if to_add[0] is None:
        break
    crossword.add(*to_add)  # type: ignore
    logger.info("Next word")

print(crossword)
print()
# TODO: Fix cached_property in order for this to work:
# print("\n".join(crossword.words))
print("\n".join(crossword.words_horizontal | crossword.words_vertical))
