import asyncio
from contextlib import suppress

from platyrhynchos.director.direct_search import generate_crossword

with suppress(ModuleNotFoundError):
    import functiontrace

    functiontrace.trace()

crossword = asyncio.run(generate_crossword(10, 10, 16))
print(crossword)
print()
print("Word amount:", len(crossword.words))
print("Words:", ",".join(crossword.words.keys()))
