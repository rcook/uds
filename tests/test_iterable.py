from __future__ import annotations

from bygge.util.iterable import find_all, find_first


def test_find_first_found() -> None:
    assert find_first([1, 2, 3, 4], lambda x: x > 2) == 3


def test_find_first_not_found() -> None:
    assert find_first([1, 2, 3], lambda x: x > 10) is None


def test_find_first_empty() -> None:
    assert find_first([], lambda x: True) is None


def test_find_all_multiple() -> None:
    assert find_all([1, 2, 3, 4, 5], lambda x: x % 2 == 0) == {2, 4}


def test_find_all_none() -> None:
    assert find_all([1, 3, 5], lambda x: x % 2 == 0) == set()


def test_find_all_all() -> None:
    assert find_all([2, 4, 6], lambda x: x % 2 == 0) == {2, 4, 6}
