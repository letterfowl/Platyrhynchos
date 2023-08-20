import asyncio
from contextlib import suppress

from platyrhynchos.scripts import direct_run

with suppress(ModuleNotFoundError):
    import functiontrace

    functiontrace.trace()

direct_run()
