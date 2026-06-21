from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from bygge.cmd.plugin_runner import PluginRunner
from bygge.cmd.run_result import RunResult
from bygge.contracts import CoveragePlugin, Payload, PluginResult, TypeCheckPlugin
from bygge.contracts import TestPlugin as _TestPlugin
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
        source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_plugins=[PytestDiscovery()],
        test_plugins=[Pytest()],
        coverage_plugins=[PytestCov()],
        type_check_plugins=[Basedpyright()],
    )


@pytest.fixture
def mock_workspace(tmp_workspace: Path) -> Workspace:
    """Create a workspace for testing."""
    return Workspace.find(cwd=tmp_workspace, workspace_dir=None)


@pytest.fixture
def mock_test_plugin() -> _TestPlugin:
    """Mock test plugin."""
    plugin = Mock(spec=_TestPlugin)
    plugin.run_test = MagicMock(return_value=True)
    return plugin


@pytest.fixture
def mock_coverage_plugin() -> CoveragePlugin:
    """Mock coverage plugin."""
    plugin = Mock(spec=CoveragePlugin)
    plugin.run_coverage = MagicMock(return_value=True)
    return plugin


@pytest.fixture
def mock_type_check_plugin() -> TypeCheckPlugin:
    """Mock type check plugin."""
    plugin = Mock(spec=TypeCheckPlugin)
    plugin.run_type_check = MagicMock(return_value=True)
    return plugin


def test_runner_initialization(
    mock_workspace: Workspace,
    mock_plugins: Plugins,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
) -> None:
    """Test Runner can be initialized with workspace and plugins."""
    runner = PluginRunner(workspace=mock_workspace, plugins=mock_plugins)
    assert runner is not None
    assert runner.workspace == mock_workspace


def test_run_test_no_plugins(
    mock_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test run_test when no test plugins are available."""
    # Use plugins with no plugins installed
    empty_plugins = Plugins(
        source_dir_plugins=[],
        test_dir_plugins=[],
        test_plugins=[],
        coverage_plugins=[],
        type_check_plugins=[],
    )
    runner = PluginRunner(workspace=mock_workspace, plugins=empty_plugins)
    result = runner.run_test(args=())

    assert isinstance(result, RunResult)
    assert result.ran is False
    assert result.succeeded is False
    assert "No test plugin ran" in caplog.text


def test_run_coverage_no_plugins(
    mock_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test run_coverage when no coverage plugins are available."""
    # Use plugins with no plugins installed
    empty_plugins = Plugins(
        source_dir_plugins=[],
        test_dir_plugins=[],
        test_plugins=[],
        coverage_plugins=[],
        type_check_plugins=[],
    )
    runner = PluginRunner(workspace=mock_workspace, plugins=empty_plugins)
    result = runner.run_coverage(args=())

    assert isinstance(result, RunResult)
    assert result.ran is False
    assert result.succeeded is False
    assert "No coverage plugin ran" in caplog.text


def test_run_type_check_no_plugins(
    mock_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test run_type_check when no type check plugins are available."""
    # Use plugins with no plugins installed
    empty_plugins = Plugins(
        source_dir_plugins=[],
        test_dir_plugins=[],
        test_plugins=[],
        coverage_plugins=[],
        type_check_plugins=[],
    )
    runner = PluginRunner(workspace=mock_workspace, plugins=empty_plugins)
    result = runner.run_type_check(args=())

    assert isinstance(result, RunResult)
    assert result.ran is False
    assert result.succeeded is False
    assert "No type check plugin ran" in caplog.text


def test_run_result_creation() -> None:
    """Test RunResult named tuple."""
    result = RunResult(ran=True, succeeded=True)
    assert result.ran is True
    assert result.succeeded is True

    result_failed = RunResult(ran=True, succeeded=False)
    assert result_failed.ran is True
    assert result_failed.succeeded is False


def test_run_plugins_with_success() -> None:
    """Test _run_plugins with successful plugin execution."""
    mock_plugin = Mock()
    payload = Payload(source_dirs=[Path("src")], test_dirs=[Path("tests")])
    plugins = {mock_plugin: payload}

    def success_fn(_plugin: Mock, _p: Payload) -> PluginResult:
        return PluginResult.PASSED

    result = PluginRunner.run_plugins(plugins=plugins, f=success_fn, label="test")
    assert result.ran is True
    assert result.succeeded is True


def test_run_plugins_with_failure() -> None:
    """Test _run_plugins with failed plugin execution."""
    mock_plugin = Mock()
    payload = Payload(source_dirs=[Path("src")], test_dirs=[Path("tests")])
    plugins = {mock_plugin: payload}

    def failure_fn(_plugin: Mock, _p: Payload) -> PluginResult:
        return PluginResult.FAILED

    result = PluginRunner.run_plugins(plugins=plugins, f=failure_fn, label="test")
    assert result.ran is True
    assert result.succeeded is False


def test_run_plugins_with_error() -> None:
    """Test _run_plugins with errored plugin execution."""
    mock_plugin = Mock()
    payload = Payload(source_dirs=[Path("src")], test_dirs=[Path("tests")])
    plugins = {mock_plugin: payload}

    def error_fn(_plugin: Mock, _p: Payload) -> PluginResult:
        return PluginResult.PLUGIN_ERROR

    result = PluginRunner.run_plugins(plugins=plugins, f=error_fn, label="test")
    assert result.ran is True
    assert result.succeeded is False


def test_run_plugins_mixed_results() -> None:
    """Test _run_plugins with mixed success/failure results."""
    mock_plugin1 = Mock()
    mock_plugin1.__class__.__name__ = "Plugin1"
    mock_plugin2 = Mock()
    mock_plugin2.__class__.__name__ = "Plugin2"

    payload = Payload(source_dirs=[Path("src")], test_dirs=[Path("tests")])
    plugins = {mock_plugin1: payload, mock_plugin2: payload}

    call_count = 0

    def mixed_fn(_plugin: Mock, _p: Payload) -> PluginResult:
        nonlocal call_count
        call_count += 1
        match call_count:
            case 1:
                return PluginResult.PASSED
            case 2:
                return PluginResult.FAILED
            case _:  # pragma: nocover
                raise AssertionError()

    result = PluginRunner.run_plugins(plugins=plugins, f=mixed_fn, label="test")
    assert result.ran is True
    assert result.succeeded is False  # Any failure means overall failure
