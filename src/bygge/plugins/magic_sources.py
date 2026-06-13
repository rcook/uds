from __future__ import annotations

from logging import warning
from pathlib import Path

from bygge.contracts import Input
from bygge.util import TomlValue


class MagicSources:
    def fetch_source_dirs(self, input: Input, blob: TomlValue) -> list[Path] | None:  # pyright: ignore[reportUnusedParameter]
        source_dir = input.pyproject_path.parent / "src"
        if source_dir.is_dir():
            warning(f"Inferring source directory {source_dir}")
            return [source_dir]

        """
        warning(
            "No explicit source directories defined in "
            + "{input.pyproject_path} and no source directory could be inferred"
        )
        return []
        """

        return None
