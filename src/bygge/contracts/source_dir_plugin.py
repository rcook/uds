from __future__ import annotations

from pathlib import Path
from typing import Protocol

from bygge.util import TomlValue

from .input import Input


class SourceDirPlugin(Protocol):
    def fetch_source_dirs(self, input: Input, blob: TomlValue) -> list[Path] | None: ...
