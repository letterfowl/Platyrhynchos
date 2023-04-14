"""Random reusable stuff"""
from __future__ import annotations
from typing import TypeVar, Callable, Any, NewType

T = TypeVar("T")
T2 = TypeVar("T2")

Coord = NewType("Coord", tuple[int, int])
IsColumn = NewType("IsColumn", bool)
ColRowId = NewType("ColRowId", int)


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
