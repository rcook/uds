from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input, Payload, PluginResult
from bygge.plugins.util import check_requirements
from bygge.run import run_subprocess
from bygge.util import TomlValue
from bygge.workspace import Workspace


class Vulture:
    def is_installed(self, input: Input, blob: TomlValue) -> bool:
        return check_requirements(input=input, blob=blob, required_deps=["vulture"])

    def run_dead_code(
        self,
        workspace: Workspace,
        payload: Payload,
        fix: bool,
        args: tuple[str, ...],
    ) -> PluginResult:
        return self.run_vulture(
            cmd=[
                str(workspace.make_bin_path("vulture")),
                *[str(p) for p in payload.source_dirs],
                *(["--make-whitelist"] if fix else []),
                *args,
            ],
            cwd=workspace.cwd,
            fix=fix,
        )

    def run_vulture(self, cmd: list[str], cwd: Path, fix: bool = False) -> PluginResult:
        proc = run_subprocess(cmd=cmd, cwd=cwd, check=False, yes=True)
        match proc.returncode:
            case 0:
                return PluginResult.PASSED
            case 1:  # pragma: no cover
                return PluginResult.FAILED
            case 3:  # pragma: no cover
                # Exit code 3: dead code found
                # In fix mode (--make-whitelist), this is success (whitelist generated)
                # In check mode, this is failure (dead code detected)
                return PluginResult.PASSED if fix else PluginResult.FAILED
            case _:  # pragma: no cover
                proc.check_returncode()
                raise AssertionError()
