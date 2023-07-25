import asyncio
from contextlib import suppress

from platyrhynchos.scripts import annealing_run

with suppress(ModuleNotFoundError):
    import functiontrace

    functiontrace.trace()

annealing_run()
