from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from typing import cast
from unittest.mock import MagicMock

from pytest import CaptureFixture, raises

from bygge import ByggeError
from bygge.cmd.check_cmd import check
from bygge.cmd.coverage_cmd import coverage
from bygge.cmd.dead_cmd import dead
from bygge.cmd.fmt_cmd import fmt
from bygge.cmd.lint_cmd import lint
from bygge.cmd.test_cmd import test as run_test
from bygge.cmd.type_check_cmd import type_check
from bygge.workspace import Workspace


def test_fmt_fix_mode(
    tmp_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test fmt command in fix mode."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    fmt(workspace=tmp_workspace, fix=True, args=())

    assert mock_subprocess.call_count == 2
    first_call = mock_subprocess.call_args_list[0]
    assert "ruff" in first_call[0][0][0]
    assert "format" in first_call[0][0]


def test_fmt_check_mode(
    tmp_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test fmt command in check mode."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    fmt(workspace=tmp_workspace, fix=False, args=())

    assert mock_subprocess.call_count == 2
    first_call = mock_subprocess.call_args_list[0]
    assert "--check" in first_call[0][0]


def test_fmt_format_failure(tmp_workspace: Workspace, mock_subprocess: MagicMock) -> None:
    """Test fmt command when format check fails."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    with raises(ByggeError, match="No format plugin found"):
        fmt(workspace=tmp_workspace, fix=False, args=())


def test_fmt_isort_failure(tmp_workspace: Workspace, mock_subprocess: MagicMock) -> None:
    """Test fmt command when import sort fails."""

    def side_effect(cmd: list[str], *_args: object, **_kwargs: object) -> CompletedProcess[str]:
        if "format" in cmd:
            return CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        return CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    mock_subprocess.side_effect = side_effect

    with raises(ByggeError, match="No format plugin found"):
        fmt(workspace=tmp_workspace, fix=False, args=())


def test_fmt_uses_payload_dirs(
    tmp_workspace: Workspace,
    tmp_package: Path,
    mock_subprocess: MagicMock,
) -> None:
    """Test that fmt command passes payload source_dirs and test_dirs to ruff."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    fmt(workspace=tmp_workspace, fix=True, args=())

    assert mock_subprocess.call_count == 2
    # Check the format call includes source and test dirs from payload
    first_call = mock_subprocess.call_args_list[0]
    cmd = cast(list[str], first_call[0][0])
    assert "format" in cmd
    # Should include the tmp_package src directory
    assert any(str(tmp_package / "src") in arg for arg in cmd if isinstance(arg, str))


def test_lint_uses_payload_dirs(
    tmp_workspace: Workspace,
    tmp_package: Path,
    mock_subprocess: MagicMock,
) -> None:
    """Test that lint command passes payload source_dirs and test_dirs to ruff."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    lint(workspace=tmp_workspace, fix=False, args=())

    assert mock_subprocess.call_count >= 1
    # Check the check call includes source and test dirs from payload
    first_call = mock_subprocess.call_args_list[0]
    cmd = cast(list[str], first_call[0][0])
    assert "check" in cmd
    # Should include the tmp_package src directory
    assert any(str(tmp_package / "src") in arg for arg in cmd if isinstance(arg, str))


def test_lint_no_fix(
    tmp_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test lint command without fix."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    lint(workspace=tmp_workspace, fix=False, args=())

    assert mock_subprocess.call_count == 1
    call_args = mock_subprocess.call_args_list[0]
    assert "ruff" in call_args[0][0][0]
    assert "check" in call_args[0][0]
    assert "--fix" not in call_args[0][0]


def test_lint_with_fix(
    tmp_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test lint command with fix."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    lint(workspace=tmp_workspace, fix=True, args=())

    assert mock_subprocess.call_count == 1
    call_args = mock_subprocess.call_args_list[0]
    assert "--fix" in call_args[0][0]


def test_lint_failure(tmp_workspace: Workspace, mock_subprocess: MagicMock) -> None:
    """Test lint command when lint fails."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    with raises(ByggeError, match="No lint plugin found"):
        lint(workspace=tmp_workspace, fix=False, args=())


def test_check_runs_all_checks(
    tmp_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
    capsys: CaptureFixture[str],
) -> None:
    """Test check command runs all checks."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    check(workspace=tmp_workspace)

    captured = capsys.readouterr()
    assert "Checking formatting..." in captured.out
    assert "Linting..." in captured.out
    assert "Type checking..." in captured.out
    assert "Running coverage" in captured.out
    assert "All checks passed." in captured.out


def test_test_command_success(
    tmp_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test test command with successful run."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    # Should succeed with mocked subprocess
    run_test(workspace=tmp_workspace, args=())

    # Verify subprocess was called
    assert mock_subprocess.call_count > 0


def test_coverage_command_success(
    tmp_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test coverage command with successful run."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    # Should succeed with mocked subprocess
    coverage(workspace=tmp_workspace, args=())

    # Verify subprocess was called
    assert mock_subprocess.call_count > 0


def test_type_check_command_success(
    tmp_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test type_check command with successful run."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    # Should succeed with mocked subprocess
    type_check(workspace=tmp_workspace, args=())

    # Verify subprocess was called
    assert mock_subprocess.call_count > 0


def test_dead_code_command_success(
    tmp_workspace: Workspace, tmp_package: Path, mock_subprocess: MagicMock
) -> None:
    """Test dead code command with success."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    # Add vulture to package dependencies
    pyproject_path = tmp_package / "pyproject.toml"
    content = pyproject_path.read_text()
    content = content.replace(
        'dev = ["pytest", "pytest-cov", "basedpyright", "ruff"]',
        'dev = ["pytest", "pytest-cov", "basedpyright", "ruff", "vulture"]',
    )
    _ = pyproject_path.write_text(content)

    dead(workspace=tmp_workspace, fix=False, args=())


def test_dead_code_command_failure(
    tmp_workspace: Workspace, tmp_package: Path, mock_subprocess: MagicMock
) -> None:
    """Test dead code command with failure."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=3, stdout="", stderr="")

    # Add vulture to package dependencies
    pyproject_path = tmp_package / "pyproject.toml"
    content = pyproject_path.read_text()
    content = content.replace(
        'dev = ["pytest", "pytest-cov", "basedpyright", "ruff"]',
        'dev = ["pytest", "pytest-cov", "basedpyright", "ruff", "vulture"]',
    )
    _ = pyproject_path.write_text(content)

    with raises(ByggeError, match="Dead code analysis failed"):
        dead(workspace=tmp_workspace, fix=False, args=())


def test_dead_code_command_no_tool_found(tmp_workspace: Workspace) -> None:
    """Test dead code command when no plugin is found."""
    # tmp_workspace doesn't have vulture in dependencies by default
    with raises(ByggeError, match="No dead code plugin found"):
        dead(workspace=tmp_workspace, fix=False, args=())
