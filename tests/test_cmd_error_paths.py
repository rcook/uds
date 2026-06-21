from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock

from pytest import raises

from bygge import ByggeError
from bygge.cmd.coverage_cmd import coverage
from bygge.cmd.test_cmd import test as run_test
from bygge.cmd.type_check_cmd import type_check
from bygge.workspace import Workspace


def test_coverage_command_failure(
    tmp_workspace: Path,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test coverage command when coverage run fails."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    with raises(ByggeError, match="Coverage run failed"):
        coverage(workspace=workspace, args=())


def test_test_command_failure(
    tmp_workspace: Path,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test test command when test run fails."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    with raises(ByggeError, match="Test run failed"):
        run_test(workspace=workspace, args=())


def test_type_check_command_failure(
    tmp_workspace: Path,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test type_check command when type check fails."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    with raises(ByggeError, match="Type check run failed"):
        type_check(workspace=workspace, args=())


def test_coverage_command_no_tool_found(tmp_workspace: Path, tmp_package: Path) -> None:  # pyright: ignore[reportUnusedParameter]
    """Test coverage command when no coverage tool is found."""
    from unittest.mock import patch

    from bygge.plugins import Plugins

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    # Mock PLUGINS to have no coverage tools
    empty_plugins = Plugins()

    with (
        patch("bygge.cmd.coverage_cmd.PLUGINS", empty_plugins),
        raises(ByggeError, match="No coverage plugin found"),
    ):
        coverage(workspace=workspace, args=())


def test_test_command_no_tool_found(tmp_workspace: Path, tmp_package: Path) -> None:  # pyright: ignore[reportUnusedParameter]
    """Test test command when no test tool is found."""
    from unittest.mock import patch

    from bygge.plugins import Plugins

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    # Mock PLUGINS to have no test tools
    empty_plugins = Plugins()

    with (
        patch("bygge.cmd.test_cmd.PLUGINS", empty_plugins),
        raises(ByggeError, match="No test plugin found"),
    ):
        run_test(workspace=workspace, args=())


def test_type_check_command_no_tool_found(tmp_workspace: Path, tmp_package: Path) -> None:  # pyright: ignore[reportUnusedParameter]
    """Test type_check command when no type check tool is found."""
    from unittest.mock import patch

    from bygge.plugins import Plugins

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    # Mock PLUGINS to have no type check tools
    empty_plugins = Plugins()

    with (
        patch("bygge.cmd.type_check_cmd.PLUGINS", empty_plugins),
        raises(ByggeError, match="No type check plugin found"),
    ):
        type_check(workspace=workspace, args=())
