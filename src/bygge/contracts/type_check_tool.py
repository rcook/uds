from __future__ import annotations

from typing import Protocol

from bygge.workspace import Workspace

from .payload import Payload
from .tool import Tool
from .tool_result import ToolResult


class TypeCheckTool(Tool, Protocol):
    def run_type_check(
        self, workspace: Workspace, payload: Payload, args: tuple[str, ...]
    ) -> ToolResult: ...
