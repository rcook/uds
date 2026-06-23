from __future__ import annotations

from typing import Never, NoReturn


def assert_never(obj: Never) -> NoReturn:  # pragma: no cover
    raise AssertionError(f"Unhandled value: {obj!r}")
