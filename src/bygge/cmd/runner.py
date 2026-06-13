from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from logging import warning
from pathlib import Path

from bygge.contracts import CoverageTool, Input, Payload, ToolResult, TypeCheckTool, UnitTestTool
from bygge.package_info import PackageInfo
from bygge.plugins import Plugins
from bygge.target_info import TargetInfo
from bygge.workspace import Workspace

from .run_result import RunResult


class Runner:
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
        test_tools: dict[UnitTestTool, PayloadBuilder] = {}
        coverage_tools: dict[CoverageTool, PayloadBuilder] = {}
        type_check_tools: dict[TypeCheckTool, PayloadBuilder] = {}
        for meta in target_info.ordered_metas:
            input = Input(pyproject_path=meta.pyproject_path, optional_deps=workspace.optional_deps)
            info = PackageInfo.make(plugins=plugins, input=input)
            if info is None:
                continue

            infos.append(info)
            if info.test is not None:
                acc = test_tools.setdefault(info.test.tool, PayloadBuilder())
                acc.extend(info.test.payload)
            if info.coverage is not None:
                acc = coverage_tools.setdefault(info.coverage.tool, PayloadBuilder())
                acc.extend(info.coverage.payload)
            if info.type_check is not None:
                acc = type_check_tools.setdefault(info.type_check.tool, PayloadBuilder())
                acc.extend(info.type_check.payload)

        self.workspace: Workspace = workspace
        self._test_tools: dict[UnitTestTool, Payload] = {
            t: b.to_payload() for t, b in test_tools.items()
        }
        self._coverage_tools: dict[CoverageTool, Payload] = {
            t: b.to_payload() for t, b in coverage_tools.items()
        }
        self._type_check_tools: dict[TypeCheckTool, Payload] = {
            t: b.to_payload() for t, b in type_check_tools.items()
        }

    def run_test(self, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_tools(
            tools=self._test_tools,
            f=lambda tool, payload: tool.run_test(
                workspace=self.workspace, payload=payload, args=args
            ),
            label="test",
        )

    def run_coverage(self, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_tools(
            tools=self._coverage_tools,
            f=lambda tool, payload: tool.run_coverage(
                workspace=self.workspace,
                payload=payload,
                args=args,
                coverage_baseline=self.workspace.coverage_baseline,
            ),
            label="coverage",
        )

    def run_type_check(self, args: tuple[str, ...]) -> RunResult:
        return self.__class__.run_tools(
            tools=self._type_check_tools,
            f=lambda tool, payload: tool.run_type_check(
                workspace=self.workspace, payload=payload, args=args
            ),
            label="type check",
        )

    @staticmethod
    def run_tools[T](
        tools: dict[T, Payload], f: Callable[[T, Payload], ToolResult], label: str
    ) -> RunResult:
        success_count = 0
        failure_count = 0
        error_count = 0

        for tool, payload in sorted(tools.items(), key=lambda p: type(p[0]).__name__):
            match f(tool, payload):
                case ToolResult.TEST_PASSED:
                    success_count += 1
                case ToolResult.TEST_FAILED:
                    failure_count += 1
                case ToolResult.TOOL_ERROR:
                    error_count += 1

        total = success_count + failure_count + error_count
        ran = total > 0
        succeeded = ran and failure_count == 0 and error_count == 0
        if not ran:
            warning(f"No {label} tool ran")

        return RunResult(ran=ran, succeeded=succeeded)
