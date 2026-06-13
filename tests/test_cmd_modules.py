from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock

import pytest

from bygge import ByggeError
from bygge.cmd.check_cmd import check
from bygge.cmd.coverage_cmd import coverage
from bygge.cmd.fmt_cmd import fmt
from bygge.cmd.lint_cmd import lint
from bygge.cmd.test_cmd import test as run_test
from bygge.cmd.type_check_cmd import type_check
from bygge.workspace import Workspace


def test_fmt_fix_mode(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test fmt command in fix mode."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    fmt(workspace=workspace, fix=True)

    assert mock_subprocess.call_count == 2
    first_call = mock_subprocess.call_args_list[0]
    assert "ruff" in first_call[0][0][0]
    assert "format" in first_call[0][0]


def test_fmt_check_mode(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test fmt command in check mode."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    fmt(workspace=workspace, fix=False)

    assert mock_subprocess.call_count == 2
    first_call = mock_subprocess.call_args_list[0]
    assert "--check" in first_call[0][0]


def test_fmt_format_failure(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test fmt command when format check fails."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    with pytest.raises(ByggeError, match="Format check failed"):
        fmt(workspace=workspace, fix=False)


def test_fmt_isort_failure(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test fmt command when import sort fails."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    def side_effect(cmd: list[str], *_args: object, **_kwargs: object) -> CompletedProcess[str]:
        if "format" in cmd:
            return CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        return CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    mock_subprocess.side_effect = side_effect

    with pytest.raises(ByggeError, match="Import sort check failed"):
        fmt(workspace=workspace, fix=False)


def test_lint_no_fix(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test lint command without fix."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    lint(workspace=workspace, fix=False, args=())

    assert mock_subprocess.call_count == 1
    call_args = mock_subprocess.call_args_list[0]
    assert "ruff" in call_args[0][0][0]
    assert "check" in call_args[0][0]
    assert "--fix" not in call_args[0][0]


def test_lint_with_fix(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test lint command with fix."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    lint(workspace=workspace, fix=True, args=())

    assert mock_subprocess.call_count == 1
    call_args = mock_subprocess.call_args_list[0]
    assert "--fix" in call_args[0][0]


def test_lint_failure(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test lint command when lint fails."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    with pytest.raises(ByggeError, match="Lint check failed"):
        lint(workspace=workspace, fix=False, args=())


def test_check_runs_all_checks(
    tmp_workspace: Path,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test check command runs all checks."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    check(workspace=workspace)

    captured = capsys.readouterr()
    assert "Checking formatting..." in captured.out
    assert "Linting..." in captured.out
    assert "Type checking..." in captured.out
    assert "Running coverage" in captured.out
    assert "All checks passed." in captured.out


def test_test_command_success(
    tmp_workspace: Path,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test test command with successful run."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    # Should succeed with mocked subprocess
    run_test(workspace=workspace, args=())

    # Verify subprocess was called
    assert mock_subprocess.call_count > 0


def test_coverage_command_success(
    tmp_workspace: Path,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test coverage command with successful run."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    # Should succeed with mocked subprocess
    coverage(workspace=workspace, args=())

    # Verify subprocess was called
    assert mock_subprocess.call_count > 0


def test_type_check_command_success(
    tmp_workspace: Path,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test type_check command with successful run."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    # Should succeed with mocked subprocess
    type_check(workspace=workspace, args=())

    # Verify subprocess was called
    assert mock_subprocess.call_count > 0
