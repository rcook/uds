from __future__ import annotations

from enum import Enum, auto, unique


@unique
class ToolResult(Enum):
    TEST_PASSED = auto()
    TEST_FAILED = auto()
    TOOL_ERROR = auto()
