from __future__ import annotations

from typing import Protocol

from bygge.util import TomlValue

from .input import Input


class Plugin(Protocol):
    def is_installed(self, input: Input, blob: TomlValue) -> bool: ...
