import asyncio
from contextlib import suppress

from platyrhynchos.scripts import local_search_run

with suppress(ModuleNotFoundError):
    import functiontrace

    functiontrace.trace()

local_search_run()
