"""Random reusable stuff"""
from __future__ import annotations

import bisect
from typing import Any, Callable, Generic, NewType, TypeVar

T = TypeVar("T")
T2 = TypeVar("T2")

Coord = NewType("Coord", tuple[int, int])
IsColumn = NewType("IsColumn", bool)
ColRowIndex = NewType("ColRowIndex", int)
ColRowId = NewType("ColRowId", tuple[IsColumn, ColRowIndex])
WordHistory = NewType("WordHistory", dict[ColRowId, set[str]])


class ProxiedDict(dict):
    """A dict that can run a function on every set or get"""

    def __init__(
        self,
        source: dict[T, T2],
        on_set: Callable[[T, T2], None] = lambda x, y: None,
        on_get: Callable[[T, T2], None] = lambda x, y: None,
    ):
        self.on_set = on_set
        self.on_get = on_get
        super().__init__(((i, j) for i, j in source.items() if on_set(i, j) or True))

    def __setitem__(self, __key: Any, __value: Any) -> None:
        self.on_set(__key, __value)
        return super().__setitem__(__key, __value)

    def __getitem__(self, __key: Any) -> Any:
        val = super().__getitem__(__key)
        self.on_get(__key, val)
        return val

    def __hash__(self) -> int:
        return hash(tuple(self.items()))


class HallOfFame(Generic[T]):
    def __init__(self, n: int):
        self.n = n
        self.solutions: list[tuple[float, T]] = []

    def add(self, score: float, solution: T):
        bisect.insort(self.solutions, (score, solution), key=lambda x: x[0])
        self.solutions = self.solutions[: self.n]

    def get_best(self) -> list[T]:
        return [solution for _, solution in self.solutions]

    def get_scores(self) -> list[float]:
        return [score for score, _ in self.solutions]

    def __iter__(self):
        return self.get_best()

    def non_empty(self):
        return bool(self.solutions)
