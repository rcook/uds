from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock

import pytest

from bygge.cmd.commit_unchecked_cmd import commit_unchecked
from bygge.cmd.hooks_cmd import hooks
from bygge.cmd.init_cmd import init
from bygge.cmd.unhook_cmd import unhook
from bygge.workspace import Workspace


def test_hooks_configures_git(
    tmp_workspace: Path, mock_subprocess: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test hooks command configures git hooks path."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    hooks(workspace=workspace)

    captured = capsys.readouterr()
    assert "Git hooks installed" in captured.out
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args_list[0]
    assert "git" in call_args[0][0]
    assert "core.hooksPath" in call_args[0][0]


def test_unhook_unsets_git_config(
    tmp_workspace: Path, mock_subprocess: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test unhook command unsets git hooks path."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    unhook(workspace=workspace)

    captured = capsys.readouterr()
    assert "Git hooks uninstalled" in captured.out
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args_list[0]
    assert "git" in call_args[0][0]
    assert "--unset" in call_args[0][0]


def test_commit_unchecked(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test commit_unchecked bypasses git hooks."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    commit_unchecked(workspace=workspace, args=("-m", "test commit"))

    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args_list[0]
    cmd: list[str] = call_args[0][0]  # pyright: ignore[reportAny]
    assert "git" in cmd
    assert "core.hooksPath=/dev/null" in cmd
    assert "commit" in cmd
    assert "-m" in cmd
    assert "test commit" in cmd


def test_init_creates_venv(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test init command creates virtual environment."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    # Remove the venv created by fixture
    import shutil

    if workspace.venv_dir.exists():
        shutil.rmtree(workspace.venv_dir)

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=workspace, reinit=False, install=False, yes=True)

    assert mock_subprocess.call_count >= 1
    first_call = mock_subprocess.call_args_list[0]
    cmd: list[str] = first_call[0][0]  # pyright: ignore[reportAny]
    assert "-m" in cmd
    assert "venv" in cmd


def test_init_with_install(
    tmp_workspace: Path,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test init command with install flag."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=workspace, reinit=False, install=True, yes=True)

    # Should call pip install for the package
    assert mock_subprocess.call_count >= 1
    pip_calls = [
        call
        for call in mock_subprocess.call_args_list
        if "pip" in str(call.args[0] if hasattr(call, "args") else call[0][0])  # pyright: ignore[reportAny]
    ]
    assert len(pip_calls) > 0


def test_init_reinit_removes_venv(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test init command with reinit flag removes existing venv."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    workspace.venv_dir.mkdir(parents=True, exist_ok=True)
    _ = (workspace.venv_dir / "marker.txt").write_text("existing")

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=workspace, reinit=True, install=False, yes=True)

    assert not (workspace.venv_dir / "marker.txt").exists()


def test_init_existing_venv_no_reinit(
    tmp_workspace: Path, mock_subprocess: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test init command preserves existing venv when reinit is False."""
    import logging

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    # Venv already exists from fixture

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    with caplog.at_level(logging.INFO):
        init(workspace=workspace, reinit=False, install=False, yes=True)

    assert "Using existing" in caplog.text


def test_init_with_requirements_file(tmp_workspace: Path, mock_subprocess: MagicMock) -> None:
    """Test init command installs requirements from requirements.txt."""
    # Create a requirements file
    _ = (tmp_workspace / "requirements-dev.txt").write_text("pytest\\nblack\\n")

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=workspace, reinit=False, install=True, yes=True)

    # Should have called pip install for requirements
    pip_calls = [
        call
        for call in mock_subprocess.call_args_list
        if "pip" in str(call.args[0] if hasattr(call, "args") else call[0][0])  # pyright: ignore[reportAny]
    ]
    requirements_calls = [
        call
        for call in pip_calls
        if "--requirement" in str(call.args[0] if hasattr(call, "args") else call[0][0])  # pyright: ignore[reportAny]
        or "requirements" in str(call.args[0] if hasattr(call, "args") else call[0][0])  # pyright: ignore[reportAny]
    ]
    assert len(requirements_calls) > 0
