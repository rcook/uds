from __future__ import annotations

from bygge.contracts import Input, Payload, PluginResult
from bygge.util import TomlValue
from bygge.workspace import Workspace

from .pytest_run_mixin import PytestRunMixin
from .util import fetch_pytest_test_dirs


class Pytest(PytestRunMixin):
    def is_installed(self, input: Input, blob: TomlValue) -> bool:
        return fetch_pytest_test_dirs(input=input, blob=blob, required_deps=["pytest"]) is not None

    def run_test(
        self,
        workspace: Workspace,
        payload: Payload,
        args: tuple[str, ...],
    ) -> PluginResult:
        cmd = [
            str(workspace.make_bin_path("pytest")),
            *[str(d) for d in sorted(payload.test_dirs)],
            "-v",
            *args,
        ]
        return self.run_pytest(cmd=cmd, cwd=workspace.workspace_dir)
