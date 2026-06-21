from __future__ import annotations

from dataclasses import dataclass, field

from bygge.contracts import (
    CoveragePlugin,
    FormatPlugin,
    LintPlugin,
    SourceDirPlugin,
    TestDirPlugin,
    TestPlugin,
    TypeCheckPlugin,
)


@dataclass(frozen=True, slots=True)
class Plugins:
    source_dir_plugins: list[SourceDirPlugin] = field(default_factory=list)
    test_dir_plugins: list[TestDirPlugin] = field(default_factory=list)
    test_plugins: list[TestPlugin] = field(default_factory=list)
    coverage_plugins: list[CoveragePlugin] = field(default_factory=list)
    type_check_plugins: list[TypeCheckPlugin] = field(default_factory=list)
    format_plugins: list[FormatPlugin] = field(default_factory=list)
    lint_plugins: list[LintPlugin] = field(default_factory=list)
