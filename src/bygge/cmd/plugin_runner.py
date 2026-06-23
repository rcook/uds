from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from logging import warning
from pathlib import Path

from bygge.contracts import (
    CoveragePlugin,
    DeadCodePlugin,
    FormatPlugin,
    Input,
    LintPlugin,
    Payload,
    PluginResult,
    TestPlugin,
    TypeCheckPlugin,
)
from bygge.package_info import PackageInfo
from bygge.plugins import Plugins
from bygge.target_info import TargetInfo
from bygge.workspace import Workspace

from .run_result import RunResult


class PluginRunner:
    def __init__(self, workspace: Workspace, plugins: Plugins) -> None:
        @dataclass(frozen=False, slots=True)
        class PayloadBuilder:
            source_dirs: list[Path] = field(default_factory=list)
            test_dirs: list[Path] = field(default_factory=list)

            def extend(self, payload: Payload) -> None:
                self.source_dirs.extend(payload.source_dirs)
                self.test_dirs.extend(payload.test_dirs)

            def to_payload(self) -> Payload:
                return Payload(source_dirs=self.source_dirs, test_dirs=self.test_dirs)

        def build[P](plugins: dict[P, PayloadBuilder]) -> dict[P, Payload]:
            return {t: b.to_payload() for t, b in plugins.items()}

        target_info = TargetInfo.build(workspace)

        infos: list[PackageInfo] = []
        test_plugins: dict[TestPlugin, PayloadBuilder] = {}
        coverage_plugins: dict[CoveragePlugin, PayloadBuilder] = {}
        type_check_plugins: dict[TypeCheckPlugin, PayloadBuilder] = {}
        format_plugins: dict[FormatPlugin, PayloadBuilder] = {}
        lint_plugins: dict[LintPlugin, PayloadBuilder] = {}
        dead_code_plugins: dict[DeadCodePlugin, PayloadBuilder] = {}
        for meta in target_info.ordered_metas:
            input = Input(
                pyproject_path=meta.pyproject_path,
                optional_deps=workspace.optional_deps,
                blob=meta.blob,
            )
            info = PackageInfo.make(plugins=plugins, input=input)
            if info is None:
                continue

            infos.append(info)
            if info.test is not None:
                acc = test_plugins.setdefault(info.test.plugin, PayloadBuilder())
                acc.extend(info.test.payload)
            if info.coverage is not None:
                acc = coverage_plugins.setdefault(info.coverage.plugin, PayloadBuilder())
                acc.extend(info.coverage.payload)
            if info.type_check is not None:
                acc = type_check_plugins.setdefault(info.type_check.plugin, PayloadBuilder())
                acc.extend(info.type_check.payload)
            if info.format is not None:
                acc = format_plugins.setdefault(info.format.plugin, PayloadBuilder())
                acc.extend(info.format.payload)
            if info.lint is not None:
                acc = lint_plugins.setdefault(info.lint.plugin, PayloadBuilder())
                acc.extend(info.lint.payload)
            if info.dead_code is not None:
                acc = dead_code_plugins.setdefault(info.dead_code.plugin, PayloadBuilder())
                acc.extend(info.dead_code.payload)

        self.workspace: Workspace = workspace
        self._infos: list[PackageInfo] = infos
        self._test_plugins: dict[TestPlugin, Payload] = build(test_plugins)
        self._coverage_plugins: dict[CoveragePlugin, Payload] = build(coverage_plugins)
        self._type_check_plugins: dict[TypeCheckPlugin, Payload] = build(type_check_plugins)
        self._format_plugins: dict[FormatPlugin, Payload] = build(format_plugins)
        self._lint_plugins: dict[LintPlugin, Payload] = build(lint_plugins)
        self._dead_code_plugins: dict[DeadCodePlugin, Payload] = build(dead_code_plugins)

    @property
    def infos(self) -> list[PackageInfo]:
        return self._infos

    def run_test(self, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_plugins(
            plugins=self._test_plugins,
            f=lambda plugin, payload: plugin.run_test(
                workspace=self.workspace, payload=payload, args=args
            ),
            label="test",
        )

    def run_coverage(self, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_plugins(
            plugins=self._coverage_plugins,
            f=lambda plugin, payload: plugin.run_coverage(
                workspace=self.workspace,
                payload=payload,
                args=args,
                coverage_baseline=self.workspace.coverage_baseline,
            ),
            label="coverage",
        )

    def run_type_check(self, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_plugins(
            plugins=self._type_check_plugins,
            f=lambda plugin, payload: plugin.run_type_check(
                workspace=self.workspace, payload=payload, args=args
            ),
            label="type check",
        )

    def run_format(self, fix: bool, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_plugins(
            plugins=self._format_plugins,
            f=lambda plugin, payload: plugin.run_format(
                workspace=self.workspace, payload=payload, fix=fix, args=args
            ),
            label="format",
        )

    def run_lint(self, fix: bool, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_plugins(
            plugins=self._lint_plugins,
            f=lambda plugin, payload: plugin.run_lint(
                workspace=self.workspace, payload=payload, fix=fix, args=args
            ),
            label="lint",
        )

    def run_dead_code(self, fix: bool, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_plugins(
            plugins=self._dead_code_plugins,
            f=lambda plugin, payload: plugin.run_dead_code(
                workspace=self.workspace, payload=payload, fix=fix, args=args
            ),
            label="dead code analysis",
        )

    @staticmethod
    def run_plugins[P](
        plugins: dict[P, Payload], f: Callable[[P, Payload], PluginResult], label: str
    ) -> RunResult:
        success_count = 0
        failure_count = 0
        error_count = 0

        for plugin, payload in sorted(plugins.items(), key=lambda p: type(p[0]).__name__):
            match f(plugin, payload):
                case PluginResult.PASSED:
                    success_count += 1
                case PluginResult.FAILED:
                    failure_count += 1
                case PluginResult.PLUGIN_ERROR:
                    error_count += 1

        total = success_count + failure_count + error_count
        ran = total > 0
        succeeded = ran and failure_count == 0 and error_count == 0
        if not ran:
            warning(f"No {label} plugin ran")

        return RunResult(ran=ran, succeeded=succeeded)
