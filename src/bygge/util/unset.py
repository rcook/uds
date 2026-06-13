from __future__ import annotations

from typing import ClassVar, Final, final


@final
class Unset:
    __slots__: Final[tuple[str, ...]] = ()

    _instance: ClassVar[Unset]

    def __new__(cls) -> Unset:
        if hasattr(cls, "_instance"):
            return cls._instance
        instance = super().__new__(cls)
        cls._instance = instance
        return instance


UNSET: Unset = Unset()
