from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input
from bygge.util import TomlValue


class MagicSources:
    def fetch_source_dirs(self, input: Input, blob: TomlValue) -> list[Path] | None:  # pyright: ignore[reportUnusedParameter]
        source_dir = input.pyproject_path.parent / "src"
        return [source_dir] if source_dir.is_dir() else None
