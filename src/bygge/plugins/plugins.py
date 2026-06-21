from __future__ import annotations

from dataclasses import dataclass

from bygge.contracts import (
    CoveragePlugin,
    SourceDirPlugin,
    TestDirPlugin,
    TestPlugin,
    TypeCheckPlugin,
)


@dataclass(frozen=True, slots=True)
class Plugins:
    source_dir_plugins: list[SourceDirPlugin]
    test_dir_plugins: list[TestDirPlugin]
    test_plugins: list[TestPlugin]
    coverage_plugins: list[CoveragePlugin]
    type_check_plugins: list[TypeCheckPlugin]
