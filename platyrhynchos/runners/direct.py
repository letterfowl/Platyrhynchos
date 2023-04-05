from random import Random
from typing import Any
from ..cruciverbalists import EnglishSimpleCruciverbalist
from ..crossword import CrosswordImprovable
import yappi

cruciverbalist = EnglishSimpleCruciverbalist()
crossword = CrosswordImprovable.make(cruciverbalist.start_word(), 10, 10)

yappi.set_clock_type("cpu")
yappi.start()
for _ in range(10):
    to_add = cruciverbalist.choose_and_fill(crossword)
    if to_add[0] is None:
        break
    crossword.add(*to_add)
yappi.stop()

print(crossword)
print()
# TODO: Fix cached_property in order for this to work:
# print("\n".join(crossword.words))
print("\n".join(crossword.words_horizontal|crossword.words_vertical))

yappi.get_func_stats().print_all()
yappi.get_thread_stats().print_all()