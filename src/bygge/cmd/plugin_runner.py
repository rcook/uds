from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from logging import warning
from pathlib import Path

from bygge.contracts import (
    CoveragePlugin,
    Input,
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

        target_info = TargetInfo.build(workspace)

        infos: list[PackageInfo] = []
        test_tools: dict[TestPlugin, PayloadBuilder] = {}
        coverage_tools: dict[CoveragePlugin, PayloadBuilder] = {}
        type_check_tools: dict[TypeCheckPlugin, PayloadBuilder] = {}
        for meta in target_info.ordered_metas:
            input = Input(pyproject_path=meta.pyproject_path, optional_deps=workspace.optional_deps)
            info = PackageInfo.make(plugins=plugins, input=input)
            if info is None:
                continue

            infos.append(info)
            if info.test is not None:
                acc = test_tools.setdefault(info.test.plugin, PayloadBuilder())
                acc.extend(info.test.payload)
            if info.coverage is not None:
                acc = coverage_tools.setdefault(info.coverage.plugin, PayloadBuilder())
                acc.extend(info.coverage.payload)
            if info.type_check is not None:
                acc = type_check_tools.setdefault(info.type_check.plugin, PayloadBuilder())
                acc.extend(info.type_check.payload)

        self.workspace: Workspace = workspace
        self._test_tools: dict[TestPlugin, Payload] = {
            t: b.to_payload() for t, b in test_tools.items()
        }
        self._coverage_tools: dict[CoveragePlugin, Payload] = {
            t: b.to_payload() for t, b in coverage_tools.items()
        }
        self._type_check_tools: dict[TypeCheckPlugin, Payload] = {
            t: b.to_payload() for t, b in type_check_tools.items()
        }

    def run_test(self, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_plugins(
            plugins=self._test_tools,
            f=lambda tool, payload: tool.run_test(
                workspace=self.workspace, payload=payload, args=args
            ),
            label="test",
        )

    def run_coverage(self, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_plugins(
            plugins=self._coverage_tools,
            f=lambda tool, payload: tool.run_coverage(
                workspace=self.workspace,
                payload=payload,
                args=args,
                coverage_baseline=self.workspace.coverage_baseline,
            ),
            label="coverage",
        )

    def run_type_check(self, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_plugins(
            plugins=self._type_check_tools,
            f=lambda tool, payload: tool.run_type_check(
                workspace=self.workspace, payload=payload, args=args
            ),
            label="type check",
        )

    @staticmethod
    def run_plugins[P](
        plugins: dict[P, Payload], f: Callable[[P, Payload], PluginResult], label: str
    ) -> RunResult:
        success_count = 0
        failure_count = 0
        error_count = 0

        for tool, payload in sorted(plugins.items(), key=lambda p: type(p[0]).__name__):
            match f(tool, payload):
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
