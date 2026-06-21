from __future__ import annotations

from logging import warning
from pathlib import Path

from bygge.contracts import PluginResult
from bygge.run import run_subprocess


class PytestRunMixin:
    def run_pytest(self, cmd: list[str], cwd: Path) -> PluginResult:
        proc = run_subprocess(cmd=cmd, cwd=cwd, check=False, yes=True)
        match proc.returncode:
            case 0:
                return PluginResult.PASSED
            case 1:
                return PluginResult.FAILED
            case 4:
                warning("One or more test directories could not be found")
                return PluginResult.PLUGIN_ERROR
            case 5:
                warning("No tests found")
                return PluginResult.PLUGIN_ERROR
            case _:  # pragma: no cover
                proc.check_returncode()
                raise AssertionError()
