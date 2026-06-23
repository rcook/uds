from __future__ import annotations

from pathlib import Path

from bygge.contracts import PluginResult
from bygge.run import run_subprocess


class RuffRunMixin:
    def run_ruff(self, cmd: list[str], cwd: Path) -> PluginResult:
        proc = run_subprocess(cmd=cmd, cwd=cwd, check=False, yes=True)
        match proc.returncode:
            case 0:
                return PluginResult.PASSED
            case 1:  # pragma: no cover
                return PluginResult.FAILED
            case _:  # pragma: no cover
                proc.check_returncode()
                raise AssertionError()
