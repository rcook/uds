from __future__ import annotations

from dataclasses import dataclass

from bygge.contracts import CoverageTool, SourceDirTool, TestDirTool, TypeCheckTool, UnitTestTool


@dataclass(frozen=True)
class Plugins:
    source_dir_tools: list[SourceDirTool]
    test_dir_tools: list[TestDirTool]
    test_tools: list[UnitTestTool]
    coverage_tools: list[CoverageTool]
    type_check_tools: list[TypeCheckTool]
