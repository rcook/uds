from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Input:
    pyproject_path: Path
    optional_deps: list[str]
