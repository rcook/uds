from __future__ import annotations

from bygge.util import UNSET, Unset


def test_unset_basics() -> None:
    a = Unset()
    b = Unset()
    assert a is b
    assert a is UNSET
