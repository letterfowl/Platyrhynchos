from contextlib import suppress

from platyrhynchos.scripts import simulated_annealing_run

with suppress(ModuleNotFoundError):
    import functiontrace

    functiontrace.trace()

simulated_annealing_run()
