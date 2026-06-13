from __future__ import annotations

from collections.abc import Callable, Iterable


def find_first[T](iterable: Iterable[T], predicate: Callable[[T], bool]) -> T | None:
    return next((item for item in iterable if predicate(item)), None)


def find_all[T](iterable: Iterable[T], predicate: Callable[[T], bool]) -> set[T]:
    return {item for item in iterable if predicate(item)}
