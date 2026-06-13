from __future__ import annotations

from logging import warning
from pathlib import Path

from bygge.contracts import ToolResult
from bygge.run import run_subprocess


class PytestRunMixin:
    def run_pytest(self, cmd: list[str], cwd: Path) -> ToolResult:
        proc = run_subprocess(cmd=cmd, cwd=cwd, check=False, yes=True)
        match proc.returncode:
            case 0:
                return ToolResult.TEST_PASSED
            case 1:
                return ToolResult.TEST_FAILED
            case 4:
                warning("One or more test directories could not be found")
                return ToolResult.TOOL_ERROR
            case 5:
                warning("No tests found")
                return ToolResult.TOOL_ERROR
            case _:  # pragma: no cover
                proc.check_returncode()
                raise AssertionError()
