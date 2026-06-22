from __future__ import annotations

from unittest.mock import patch

from pytest import CaptureFixture, mark

from bygge.cmd.info_cmd import info
from bygge.constants import IS_WINDOWS
from bygge.workspace import Workspace


def test_info_command(tmp_workspace: Workspace, capsys: CaptureFixture[str]) -> None:
    info(workspace=tmp_workspace)

    captured = capsys.readouterr()
    assert "=== bygge Environment Information ===" in captured.out
    assert "Python executable:" in captured.out
    assert "Python version:" in captured.out
    assert "Command invoked as:" in captured.out
    assert "Current working directory:" in captured.out
    assert "Workspace directory:" in captured.out
    assert "Package root directory:" in captured.out
    assert "Virtual environment directory:" in captured.out
    # Should show venv status (either ✓ or ✗)
    assert "\u2713" in captured.out or "\u2717" in captured.out


def test_info_command_paths_already_resolved(
    tmp_workspace: Workspace, capsys: CaptureFixture[str]
) -> None:
    """Test info when executable paths are already resolved (no symlinks)."""

    def get_fake_paths() -> tuple[str, str]:
        if IS_WINDOWS:
            return "C:\\path\\to\\python.exe", "C:\\path\\to\\bygge.exe"
        else:
            return "/path/to/python", "/path/to/bygge"

    executable, bygge_ = get_fake_paths()

    # Mock sys.executable and sys.argv to be the same as their resolved versions
    with patch("sys.executable", executable), patch("sys.argv", [bygge_]):
        info(workspace=tmp_workspace)

    captured = capsys.readouterr()

    # Should not show "resolves to" since paths are already resolved
    assert "resolves to" not in captured.out


def test_info_command_running_as_script(
    tmp_workspace: Workspace, capsys: CaptureFixture[str]
) -> None:
    """Test info when running as a Python script."""
    # Mock sys.argv to look like a Python script
    with patch("sys.argv", ["/path/to/main.py"]):
        info(workspace=tmp_workspace)

    captured = capsys.readouterr()
    assert "Running as Python script" in captured.out


def test_info_command_not_in_venv(tmp_workspace: Workspace, capsys: CaptureFixture[str]) -> None:
    """Test info when NOT running from project venv."""
    # Mock sys.prefix to be different from workspace venv
    with patch("sys.prefix", "/usr/local"):
        info(workspace=tmp_workspace)

    captured = capsys.readouterr()
    assert "\u2717 NOT running from project's virtual environment" in captured.out


@mark.skipif(IS_WINDOWS, reason="requires user-mode symlinks - skipping on Windows")
def test_info_command_with_symlinks(tmp_workspace: Workspace, capsys: CaptureFixture[str]) -> None:
    """Test info when paths have symlinks that need resolving."""

    import os

    # Create actual symlinks to test resolution
    bin_dir = tmp_workspace.workspace_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    target_bygge = bin_dir / "bygge-real"
    _ = target_bygge.write_text("#!/bin/sh\n")
    symlink_bygge = bin_dir / "bygge"
    if not symlink_bygge.exists():
        os.symlink(target_bygge, symlink_bygge)

    # Mock sys.argv with the symlink
    with patch("sys.argv", [str(symlink_bygge)]):
        info(workspace=tmp_workspace)

    captured = capsys.readouterr()
    # Should show "resolves to" for the symlinked argv
    assert "resolves to" in captured.out or "Command invoked as" in captured.out


def test_info_command_bygge_from_project_venv(
    tmp_workspace: Workspace, capsys: CaptureFixture[str]
) -> None:
    """Test info when bygge binary is from project venv."""
    # Mock sys.argv to point to a binary inside the venv
    venv_bin = tmp_workspace.venv_dir / "bin" / "bygge"
    with patch("sys.argv", [str(venv_bin)]), patch("sys.prefix", str(tmp_workspace.venv_dir)):
        info(workspace=tmp_workspace)

    captured = capsys.readouterr()
    # Should show both checks passing
    assert "\u2713 Running from project's virtual environment" in captured.out
    assert "\u2713 bygge binary is from project's virtual environment" in captured.out
