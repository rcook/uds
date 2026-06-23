from __future__ import annotations

from pathlib import Path

from bygge.constants import INIT_FILE_NAME, TEST_DIRS
from bygge.contracts import Input
from bygge.plugins.algorithms import remove_redundant_prefixes
from bygge.util import TomlValue, walk_dir


class MagicSources:
    def fetch_source_dirs(self, input: Input, blob: TomlValue) -> list[Path] | None:  # pyright: ignore[reportUnusedParameter]
        start_dir = input.pyproject_path.parent

        source_dir = start_dir / "src"
        if source_dir.is_dir():
            return [source_dir]

        source_dirs: list[Path] = []
        for dir, file_names in walk_dir(start_dir):
            if dir.name in TEST_DIRS:
                continue
            if INIT_FILE_NAME in file_names:
                source_dirs.append(dir)

        result = sorted(
            Path(*p)
            for p in remove_redundant_prefixes({source_dir.parts for source_dir in source_dirs})
        )

        return None if len(result) == 0 else result
