from __future__ import annotations

import shutil
import sys
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock

from pytest import CaptureFixture, LogCaptureFixture, MonkeyPatch, raises

from bygge import ByggeError
from bygge.cmd.commit_unchecked_cmd import commit_unchecked
from bygge.cmd.hook_cmd import hook
from bygge.cmd.init_cmd import init
from bygge.cmd.unhook_cmd import unhook
from bygge.workspace import Workspace


def test_hook_configures_git_and_creates_pre_commit_hook(
    tmp_workspace: Workspace, mock_subprocess: MagicMock, capsys: CaptureFixture[str]
) -> None:
    """Test hooks command configures git hooks path."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    pre_commit_path = tmp_workspace.workspace_dir / "hooks" / "pre-commit"
    assert not pre_commit_path.exists()

    pre_commit_path.parent.mkdir(parents=True)
    _ = pre_commit_path.write_text("content")

    with raises(ByggeError, match=r"^Pre-commit hook file .+ already exists$"):
        hook(workspace=tmp_workspace, dir=None, create_pre_commit=True)

    assert pre_commit_path.read_text() == "content"
    pre_commit_path.unlink()

    hook(workspace=tmp_workspace, dir=None, create_pre_commit=True)
    assert pre_commit_path.is_file() and pre_commit_path.read_text() != "content"

    captured = capsys.readouterr()
    assert "Git hooks installed" in captured.out
    assert mock_subprocess.call_count == 3

    call_args = mock_subprocess.call_args_list[0]
    assert "git" in call_args[0][0]
    assert "core.hooksPath" in call_args[0][0]

    call_args = mock_subprocess.call_args_list[1]
    assert "git" in call_args[0][0]
    assert "core.hooksPath" in call_args[0][0]

    call_args = mock_subprocess.call_args_list[2]
    assert "git" in call_args[0][0]
    assert "add" in call_args[0][0]
    assert "--chmod=+x" in call_args[0][0]


def test_unhook_unsets_git_config(
    tmp_workspace: Workspace, mock_subprocess: MagicMock, capsys: CaptureFixture[str]
) -> None:
    """Test unhook command unsets git hooks path."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    unhook(workspace=tmp_workspace)

    captured = capsys.readouterr()
    assert "Git hooks uninstalled" in captured.out
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args_list[0]
    assert "git" in call_args[0][0]
    assert "--unset" in call_args[0][0]


def test_commit_unchecked(tmp_workspace: Workspace, mock_subprocess: MagicMock) -> None:
    """Test commit_unchecked bypasses git hooks."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    commit_unchecked(workspace=tmp_workspace, args=("-m", "test commit"))

    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args_list[0]
    cmd: list[str] = call_args[0][0]  # pyright: ignore[reportAny]
    assert "git" in cmd
    assert "core.hooksPath=/dev/null" in cmd
    assert "commit" in cmd
    assert "-m" in cmd
    assert "test commit" in cmd


def test_init_creates_venv(tmp_workspace: Workspace, mock_subprocess: MagicMock) -> None:
    """Test init command creates virtual environment."""
    if tmp_workspace.venv_dir.exists():
        shutil.rmtree(tmp_workspace.venv_dir)

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=tmp_workspace, reinit=False, install=False, yes=True)

    assert mock_subprocess.call_count >= 1
    first_call = mock_subprocess.call_args_list[0]
    cmd: list[str] = first_call[0][0]  # pyright: ignore[reportAny]
    assert "-m" in cmd
    assert "venv" in cmd


def test_init_with_install(
    tmp_workspace: Workspace,
    tmp_package: Path,  # pyright: ignore[reportUnusedParameter]
    mock_subprocess: MagicMock,
) -> None:
    """Test init command with install flag."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=tmp_workspace, reinit=False, install=True, yes=True)

    # Should call pip install for the package
    assert mock_subprocess.call_count >= 1
    pip_calls = [
        call
        for call in mock_subprocess.call_args_list
        if "pip" in str(call.args[0] if hasattr(call, "args") else call[0][0])  # pyright: ignore[reportAny]
    ]
    assert len(pip_calls) > 0


def test_init_reinit_removes_venv(tmp_workspace: Workspace, mock_subprocess: MagicMock) -> None:
    """Test init command with reinit flag removes existing venv."""
    tmp_workspace.venv_dir.mkdir(parents=True, exist_ok=True)
    _ = (tmp_workspace.venv_dir / "marker.txt").write_text("existing")

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=tmp_workspace, reinit=True, install=False, yes=True)

    assert not (tmp_workspace.venv_dir / "marker.txt").exists()


def test_init_existing_venv_no_reinit(
    tmp_workspace: Workspace, mock_subprocess: MagicMock, caplog: LogCaptureFixture
) -> None:
    """Test init command preserves existing venv when reinit is False."""
    import logging

    # Venv already exists from fixture

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    with caplog.at_level(logging.INFO):
        init(workspace=tmp_workspace, reinit=False, install=False, yes=True)

    assert "Using existing" in caplog.text


def test_init_with_requirements_file(tmp_workspace_dir: Path, mock_subprocess: MagicMock) -> None:
    """Test init command installs requirements from requirements.txt."""
    # Create a requirements file
    _ = (tmp_workspace_dir / "requirements-dev.txt").write_text("pytest\\nblack\\n")

    workspace = Workspace.open(tmp_workspace_dir)
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


def test_init_python_version_exact_match(
    tmp_workspace_dir: Path, mock_subprocess: MagicMock
) -> None:
    """Test init with .python-version that exactly matches current Python."""
    shutil.rmtree(tmp_workspace_dir / ".venv")
    actual = sys.version.split()[0]
    _ = (tmp_workspace_dir / ".python-version").write_text(actual + "\n")
    workspace = Workspace.open(tmp_workspace_dir)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=workspace, reinit=False, install=False, yes=True)

    assert mock_subprocess.call_count >= 1


def test_init_python_version_prefix_match(
    tmp_workspace_dir: Path, mock_subprocess: MagicMock
) -> None:
    """Test init with .python-version that matches major.minor of current Python."""
    shutil.rmtree(tmp_workspace_dir / ".venv")
    major_minor = ".".join(sys.version.split()[0].split(".")[:2])
    _ = (tmp_workspace_dir / ".python-version").write_text(major_minor + "\n")
    workspace = Workspace.open(tmp_workspace_dir)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=workspace, reinit=False, install=False, yes=True)

    assert mock_subprocess.call_count >= 1


def test_init_python_version_mismatch(tmp_workspace_dir: Path, mock_subprocess: MagicMock) -> None:
    """Test init with .python-version that does not match current Python."""
    shutil.rmtree(tmp_workspace_dir / ".venv")
    _ = (tmp_workspace_dir / ".python-version").write_text("2.7\n")
    workspace = Workspace.open(tmp_workspace_dir)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    with raises(ByggeError, match="Python version mismatch"):
        init(workspace=workspace, reinit=False, install=False, yes=True)

    mock_subprocess.assert_not_called()


def test_init_existing_venv_skips_version_check(
    tmp_workspace_dir: Path, mock_subprocess: MagicMock, caplog: LogCaptureFixture
) -> None:
    """Test init with existing venv does not check .python-version."""
    import logging

    _ = (tmp_workspace_dir / ".python-version").write_text("2.7\n")
    workspace = Workspace.open(tmp_workspace_dir)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    with caplog.at_level(logging.INFO):
        init(workspace=workspace, reinit=False, install=False, yes=True)

    assert "Using existing" in caplog.text


def test_init_reinit_checks_python_version(
    tmp_workspace_dir: Path, mock_subprocess: MagicMock
) -> None:
    """Test init with reinit checks .python-version before recreating venv."""
    _ = (tmp_workspace_dir / ".python-version").write_text("2.7\n")
    workspace = Workspace.open(tmp_workspace_dir)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    with raises(ByggeError, match="Python version mismatch"):
        init(workspace=workspace, reinit=True, install=False, yes=True)


def test_init_python_version_empty_file(
    tmp_workspace_dir: Path, mock_subprocess: MagicMock
) -> None:
    """Test init with empty .python-version file proceeds normally."""
    shutil.rmtree(tmp_workspace_dir / ".venv")
    _ = (tmp_workspace_dir / ".python-version").write_text("   \n")
    workspace = Workspace.open(tmp_workspace_dir)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=workspace, reinit=False, install=False, yes=True)

    assert mock_subprocess.call_count >= 1


def test_init_python_version_no_file(tmp_workspace_dir: Path, mock_subprocess: MagicMock) -> None:
    """Test init without .python-version file proceeds normally."""
    shutil.rmtree(tmp_workspace_dir / ".venv")
    workspace = Workspace.open(tmp_workspace_dir)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    init(workspace=workspace, reinit=False, install=False, yes=True)

    assert mock_subprocess.call_count >= 1


def test_init_python_version_unreadable(
    tmp_workspace_dir: Path, mock_subprocess: MagicMock, monkeypatch: MonkeyPatch
) -> None:
    """Test init with unreadable .python-version file raises ByggeError."""
    shutil.rmtree(tmp_workspace_dir / ".venv")
    python_version_path = tmp_workspace_dir / ".python-version"
    _ = python_version_path.write_text("3.14\n")
    workspace = Workspace.open(tmp_workspace_dir)
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    # Mock read_text to raise OSError
    original_read_text = Path.read_text

    def mock_read_text(self: Path, *args: object, **kwargs: object) -> str:
        if self == python_version_path:
            raise OSError("Permission denied")
        return original_read_text(self, *args, **kwargs)  # pyright: ignore[reportArgumentType]

    monkeypatch.setattr(Path, "read_text", mock_read_text)

    with raises(ByggeError, match=r"Cannot read .*/\.python-version: Permission denied"):
        init(workspace=workspace, reinit=False, install=False, yes=True)
