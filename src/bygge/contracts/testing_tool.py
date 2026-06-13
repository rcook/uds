from __future__ import annotations

from typing import Protocol

from bygge.workspace import Workspace

from .payload import Payload
from .tool import Tool
from .tool_result import ToolResult


class UnitTestTool(Tool, Protocol):
    def run_test(
        self,
        workspace: Workspace,
        payload: Payload,
        args: tuple[str, ...],
    ) -> ToolResult: ...
