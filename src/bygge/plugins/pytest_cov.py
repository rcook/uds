from __future__ import annotations

from bygge.contracts import Input, Payload, PluginResult
from bygge.util import TomlValue
from bygge.workspace import Workspace

from .pytest_run_mixin import PytestRunMixin
from .test_dirs_mixin import TestDirsMixin
from .util import fetch_pytest_test_dirs


class PytestCov(TestDirsMixin, PytestRunMixin):
    def is_installed(self, input: Input, blob: TomlValue) -> bool:
        return (
            fetch_pytest_test_dirs(input=input, blob=blob, required_deps=["pytest", "pytest-cov"])
            is not None
        )

    def run_coverage(
        self,
        workspace: Workspace,
        payload: Payload,
        args: tuple[str, ...],
        coverage_baseline: int | None,
    ) -> PluginResult:
        cmd = [
            str(workspace.make_bin_path("pytest")),
            *[str(d) for d in sorted(payload.test_dirs)],
            *[f"--cov={d}" for d in sorted(payload.source_dirs)],
            "--cov-report=html",
            "--cov-report=term-missing",
            *([] if coverage_baseline is None else [f"--cov-fail-under={coverage_baseline}"]),
            *args,
        ]
        return self.run_pytest(cmd=cmd, cwd=workspace.workspace_dir)
