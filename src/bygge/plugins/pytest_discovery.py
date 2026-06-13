from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input
from bygge.util import TomlValue

from .util import fetch_pytest_test_dirs


class PytestDiscovery:
    def fetch_test_dirs(self, input: Input, blob: TomlValue) -> list[Path] | None:
        return fetch_pytest_test_dirs(input=input, blob=blob, required_deps=["pytest"])
