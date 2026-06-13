from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Payload:
    source_dirs: list[Path]
    test_dirs: list[Path]
