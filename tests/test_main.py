from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Self, cast

import click
import pytest
from click import Command
from click.testing import CliRunner
from pytest import LogCaptureFixture, MonkeyPatch

from bygge import ByggeError
from bygge.main import commit_unchecked_cmd, coverage_cmd, lint_cmd, type_check_cmd
from bygge.main import test_cmd as __test_cmd


@dataclass(frozen=False, slots=True)
class _Capture:
    called: bool = False
    args: object = None
    kwargs: object = None

    @classmethod
    def intercept(cls: type[Self], monkeypatch: MonkeyPatch, obj: object, name: str) -> Self:
        assert hasattr(obj, name)

        capture = cls()

        def interceptor(*args: object, **kwargs: object) -> None:
            capture.called = True
            capture.args = args
            capture.kwargs = kwargs

        monkeypatch.setattr(obj, name, interceptor)
        return capture


@pytest.mark.parametrize(
    "cmd_under_test, expected_extra_kwargs",
    [
        (commit_unchecked_cmd, None),
        (coverage_cmd, None),
        (lint_cmd, {"fix": False}),
        (__test_cmd, None),
        (type_check_cmd, None),
    ],
)
def test_extra_args(
    cmd_under_test: Command,
    expected_extra_kwargs: dict[str, object] | None,
    monkeypatch: MonkeyPatch,
) -> None:
    capture = _Capture.intercept(monkeypatch=monkeypatch, obj=cmd_under_test, name="callback")

    runner = CliRunner()
    result = runner.invoke(cmd_under_test, ["one", '"two three"', "--flag=val", "four"])
    assert cast(object, result.return_value) is None

    assert capture.called
    assert capture.args == ()

    expected_kwargs: dict[str, object | tuple[str, ...]] = {
        "args": ("one", '"two three"', "--flag=val", "four")
    }
    if expected_extra_kwargs:
        expected_kwargs.update(expected_extra_kwargs)
    assert capture.kwargs == expected_kwargs


def test_bygge_group_catches_bygge_error() -> None:
    """Test that ByggeGroup catches ByggeError and converts to ClickException."""
    from bygge.main import ByggeGroup

    # Create a test command that raises ByggeError
    @click.command()
    def failing_command() -> None:
        raise ByggeError("Test error message")

    # Create a group using ByggeGroup
    @click.group(cls=ByggeGroup)
    def test_group() -> None:
        pass

    test_group.add_command(failing_command, name="fail")

    # Invoke the command
    runner = CliRunner()
    result = runner.invoke(test_group, ["fail"])

    # The ByggeError should be caught and converted to ClickException
    assert result.exit_code == 1
    assert "Error: Test error message" in result.output


def test_bygge_group_flexible_option_placement() -> None:
    """Test that group-level options can appear after the subcommand."""
    from bygge.main import ByggeGroup

    # Create a group with an option
    @click.group(cls=ByggeGroup)
    @click.option("--level", default="info")
    @click.pass_context
    def test_group(ctx: click.Context, level: str) -> None:
        ctx.obj = level

    # Create a subcommand
    @test_group.command()
    @click.pass_obj
    def sub(obj: str) -> None:  # pyright: ignore[reportUnusedFunction]
        click.echo(f"level={obj}")

    runner = CliRunner()

    # Test traditional order: option before subcommand
    result1 = runner.invoke(test_group, ["--level", "debug", "sub"])
    assert result1.exit_code == 0
    assert "level=debug" in result1.output

    # Test flexible order: option after subcommand
    result2 = runner.invoke(test_group, ["sub", "--level", "debug"])
    assert result2.exit_code == 0
    assert "level=debug" in result2.output

    # Test default value
    result3 = runner.invoke(test_group, ["sub"])
    assert result3.exit_code == 0
    assert "level=info" in result3.output


def test_bygge_group_flexible_with_flag_options() -> None:
    """Test flexible placement with flag options."""
    from bygge.main import ByggeGroup

    @click.group(cls=ByggeGroup)
    @click.option("--verbose/--no-verbose", default=False)
    @click.pass_context
    def test_group(ctx: click.Context, verbose: bool) -> None:
        ctx.obj = verbose

    @test_group.command()
    @click.pass_obj
    def sub(obj: bool) -> None:  # pyright: ignore[reportUnusedFunction]
        click.echo(f"verbose={obj}")

    runner = CliRunner()

    # Flag option after subcommand
    result = runner.invoke(test_group, ["sub", "--verbose"])
    assert result.exit_code == 0
    assert "verbose=True" in result.output


def test_is_running_from_project_venv(tmp_workspace: Path) -> None:
    """Test _is_running_from_project_venv function."""
    from bygge.main import _is_running_from_project_venv  # pyright: ignore[reportPrivateUsage]
    from bygge.workspace import Workspace

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    # Since we're running tests from the project venv, this should be True
    result = _is_running_from_project_venv(workspace)
    assert isinstance(result, bool)


def test_log_executable_info(caplog: LogCaptureFixture) -> None:
    """Test _log_executable_info function."""
    import logging

    from bygge.main import _log_executable_info  # pyright: ignore[reportPrivateUsage]

    caplog.set_level(logging.DEBUG)
    _log_executable_info()

    # Should have logged something about executables
    assert any("Python executable" in record.message for record in caplog.records)
    assert any("Command invoked as" in record.message for record in caplog.records)


def test_get_delegate_venv_bygge_path_no_binary(
    tmp_workspace: Path, caplog: LogCaptureFixture
) -> None:
    """Test _should_delegate_to_venv_bygge when venv exists but has no bygge binary."""
    import logging

    from bygge.main import _get_delegate_venv_bygge_path  # pyright: ignore[reportPrivateUsage]
    from bygge.workspace import Workspace

    caplog.set_level(logging.DEBUG)
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    # The tmp workspace venv exists but has no bygge binary, should return False
    result = _get_delegate_venv_bygge_path(workspace)
    assert result is None
    # Should warn about missing bygge binary
    assert any("bygge not found" in record.message for record in caplog.records)


def test_get_delegate_venv_bygge_path_no_venv(
    tmp_workspace: Path, caplog: LogCaptureFixture
) -> None:
    """Test _should_delegate_to_venv_bygge when venv doesn't exist."""
    import logging
    import shutil

    from bygge.main import _get_delegate_venv_bygge_path  # pyright: ignore[reportPrivateUsage]
    from bygge.workspace import Workspace

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    # Remove the venv directory
    venv_dir = workspace.venv_dir
    if venv_dir.exists():
        shutil.rmtree(venv_dir)

    caplog.set_level(logging.DEBUG)
    result = _get_delegate_venv_bygge_path(workspace)
    assert result is None
    # Should log that no venv was found
    assert any("No virtual environment found" in record.message for record in caplog.records)


def test_log_executable_info_with_symlinks(caplog: LogCaptureFixture) -> None:
    """Test _log_executable_info with symlinked paths."""
    import logging
    from unittest.mock import patch

    from bygge.main import _log_executable_info  # pyright: ignore[reportPrivateUsage]

    caplog.set_level(logging.DEBUG)

    # Mock to simulate symlinks
    with (
        patch("sys.executable", "/tmp/.venv/bin/python"),
        patch("sys.argv", ["/tmp/.venv/bin/bygge"]),
    ):
        _log_executable_info()
    # Should log with arrow notation for symlinks
    messages = [r.message for r in caplog.records]
    assert any("->" in msg or "Python executable" in msg for msg in messages)


def test_log_executable_info_python_script(caplog: LogCaptureFixture) -> None:
    """Test _log_executable_info when running as Python script."""
    import logging
    from unittest.mock import patch

    from bygge.main import _log_executable_info  # pyright: ignore[reportPrivateUsage]

    caplog.set_level(logging.DEBUG)

    # Mock to simulate running as a .py script
    with patch("sys.argv", ["/path/to/script.py"]):
        _log_executable_info()
    # Should log about running as Python script
    messages = [r.message for r in caplog.records]
    assert any("Running as Python script" in msg for msg in messages)
