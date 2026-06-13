from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from bygge.cmd.run_result import RunResult
from bygge.cmd.runner import Runner
from bygge.contracts import CoverageTool, Payload, ToolResult, TypeCheckTool, UnitTestTool
from bygge.plugins import Plugins
from bygge.workspace import Workspace


@pytest.fixture
def mock_plugins() -> Plugins:
    """Mock plugins for testing."""
    from bygge.plugins import (
        Basedpyright,
        Hatchling,
        MagicSources,
        Pytest,
        PytestCov,
        PytestDiscovery,
        Setuptools,
    )

    return Plugins(
        source_dir_tools=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_tools=[PytestDiscovery()],
        test_tools=[Pytest()],
        coverage_tools=[PytestCov()],
        type_check_tools=[Basedpyright()],
    )


@pytest.fixture
def mock_workspace(tmp_workspace: Path) -> Workspace:
    """Create a workspace for testing."""
    return Workspace.find(cwd=tmp_workspace, workspace_dir=None)


@pytest.fixture
def mock_test_tool() -> UnitTestTool:
    """Mock test tool."""
    tool = Mock(spec=UnitTestTool)
    tool.run_test = MagicMock(return_value=True)
    return tool


@pytest.fixture
def mock_coverage_tool() -> CoverageTool:
    """Mock coverage tool."""
    tool = Mock(spec=CoverageTool)
    tool.run_coverage = MagicMock(return_value=True)
    return tool


@pytest.fixture
def mock_type_check_tool() -> TypeCheckTool:
    """Mock type check tool."""
    tool = Mock(spec=TypeCheckTool)
    tool.run_type_check = MagicMock(return_value=True)
    return tool


def test_runner_initialization(
    mock_workspace: Workspace,
    mock_plugins: Plugins,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
) -> None:
    """Test Runner can be initialized with workspace and plugins."""
    runner = Runner(workspace=mock_workspace, plugins=mock_plugins)
    assert runner is not None
    assert runner.workspace == mock_workspace


def test_run_test_no_tools(
    mock_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test run_test when no test tools are available."""
    # Use plugins with no tools installed
    empty_plugins = Plugins(
        source_dir_tools=[],
        test_dir_tools=[],
        test_tools=[],
        coverage_tools=[],
        type_check_tools=[],
    )
    runner = Runner(workspace=mock_workspace, plugins=empty_plugins)
    result = runner.run_test(args=())

    assert isinstance(result, RunResult)
    assert result.ran is False
    assert result.succeeded is False
    assert "No test tool ran" in caplog.text


def test_run_coverage_no_tools(
    mock_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test run_coverage when no coverage tools are available."""
    # Use plugins with no tools installed
    empty_plugins = Plugins(
        source_dir_tools=[],
        test_dir_tools=[],
        test_tools=[],
        coverage_tools=[],
        type_check_tools=[],
    )
    runner = Runner(workspace=mock_workspace, plugins=empty_plugins)
    result = runner.run_coverage(args=())

    assert isinstance(result, RunResult)
    assert result.ran is False
    assert result.succeeded is False
    assert "No coverage tool ran" in caplog.text


def test_run_type_check_no_tools(
    mock_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test run_type_check when no type check tools are available."""
    # Use plugins with no tools installed
    empty_plugins = Plugins(
        source_dir_tools=[],
        test_dir_tools=[],
        test_tools=[],
        coverage_tools=[],
        type_check_tools=[],
    )
    runner = Runner(workspace=mock_workspace, plugins=empty_plugins)
    result = runner.run_type_check(args=())

    assert isinstance(result, RunResult)
    assert result.ran is False
    assert result.succeeded is False
    assert "No type check tool ran" in caplog.text


def test_run_result_creation() -> None:
    """Test RunResult named tuple."""
    result = RunResult(ran=True, succeeded=True)
    assert result.ran is True
    assert result.succeeded is True

    result_failed = RunResult(ran=True, succeeded=False)
    assert result_failed.ran is True
    assert result_failed.succeeded is False


def test_run_tools_with_success() -> None:
    """Test _run_tools with successful tool execution."""
    mock_tool = Mock()
    payload = Payload(source_dirs=[Path("src")], test_dirs=[Path("tests")])
    tools = {mock_tool: payload}

    def success_fn(_tool: Mock, _p: Payload) -> ToolResult:
        return ToolResult.TEST_PASSED

    result = Runner.run_tools(tools=tools, f=success_fn, label="test")
    assert result.ran is True
    assert result.succeeded is True


def test_run_tools_with_failure() -> None:
    """Test _run_tools with failed tool execution."""
    mock_tool = Mock()
    payload = Payload(source_dirs=[Path("src")], test_dirs=[Path("tests")])
    tools = {mock_tool: payload}

    def failure_fn(_tool: Mock, _p: Payload) -> ToolResult:
        return ToolResult.TEST_FAILED

    result = Runner.run_tools(tools=tools, f=failure_fn, label="test")
    assert result.ran is True
    assert result.succeeded is False


def test_run_tools_with_error() -> None:
    """Test _run_tools with errored tool execution."""
    mock_tool = Mock()
    payload = Payload(source_dirs=[Path("src")], test_dirs=[Path("tests")])
    tools = {mock_tool: payload}

    def error_fn(_tool: Mock, _p: Payload) -> ToolResult:
        return ToolResult.TOOL_ERROR

    result = Runner.run_tools(tools=tools, f=error_fn, label="test")
    assert result.ran is True
    assert result.succeeded is False


def test_run_tools_mixed_results() -> None:
    """Test _run_tools with mixed success/failure results."""
    mock_tool1 = Mock()
    mock_tool1.__class__.__name__ = "Tool1"
    mock_tool2 = Mock()
    mock_tool2.__class__.__name__ = "Tool2"

    payload = Payload(source_dirs=[Path("src")], test_dirs=[Path("tests")])
    tools = {mock_tool1: payload, mock_tool2: payload}

    call_count = 0

    def mixed_fn(_tool: Mock, _p: Payload) -> ToolResult:
        nonlocal call_count
        call_count += 1
        match call_count:
            case 1:
                return ToolResult.TEST_PASSED
            case 2:
                return ToolResult.TEST_FAILED
            case _:  # pragma: nocover
                raise AssertionError()

    result = Runner.run_tools(tools=tools, f=mixed_fn, label="test")
    assert result.ran is True
    assert result.succeeded is False  # Any failure means overall failure
