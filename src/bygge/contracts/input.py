from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bygge.util import TomlValue


@dataclass(frozen=True)
class Input:
    pyproject_path: Path
    optional_deps: list[str]
    blob: TomlValue
