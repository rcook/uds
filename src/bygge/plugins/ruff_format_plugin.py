from __future__ import annotations

from bygge.contracts import Input, Payload, PluginResult
from bygge.plugins.ruff_run_mixin import RuffRunMixin
from bygge.plugins.util import check_requirements
from bygge.util import TomlValue
from bygge.workspace import Workspace


class RuffFormatPlugin(RuffRunMixin):
    def is_installed(self, input: Input, blob: TomlValue) -> bool:
        return check_requirements(input=input, blob=blob, required_deps=["ruff"])

    def run_format(
        self,
        workspace: Workspace,
        payload: Payload,
        fix: bool,
        args: tuple[str, ...],
    ) -> PluginResult:
        result0 = self._run_format_inner(workspace=workspace, payload=payload, fix=fix, args=args)
        if result0 is not PluginResult.PASSED:  # pragma: no cover
            return result0

        result1 = self._run_isort_inner(workspace=workspace, payload=payload, fix=fix, args=args)
        return result1

    def _run_format_inner(
        self,
        workspace: Workspace,
        payload: Payload,
        fix: bool,
        args: tuple[str, ...],
    ) -> PluginResult:
        return self.run_ruff(
            cmd=[
                str(workspace.make_bin_path("ruff")),
                "format",
                *([] if fix else ["--check"]),
                *[str(p) for p in payload.source_dirs],
                *[str(p) for p in payload.test_dirs],
                *args,
            ],
            cwd=workspace.cwd,
        )

    def _run_isort_inner(
        self,
        workspace: Workspace,
        payload: Payload,
        fix: bool,
        args: tuple[str, ...],
    ) -> PluginResult:
        return self.run_ruff(
            cmd=[
                str(workspace.make_bin_path("ruff")),
                "check",
                "--select",
                "I",
                *(["--fix"] if fix else []),
                *[str(p) for p in payload.source_dirs],
                *[str(p) for p in payload.test_dirs],
                *args,
            ],
            cwd=workspace.cwd,
        )
