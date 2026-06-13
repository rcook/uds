from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

from bygge.run import run_subprocess


def test_run_subprocess_yes_mode() -> None:
    with patch("bygge.run.subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess(args=["ls"], returncode=0)
        result = run_subprocess(["ls", "-la"], cwd=Path("/tmp"), check=True, yes=True)
        assert result.returncode == 0
        mock_run.assert_called_once()


def test_run_subprocess_dry_run_mode() -> None:
    _ = run_subprocess(["dangerous", "command"], cwd=Path("/tmp"), check=True, yes=False)
    # In dry-run, no actual command is executed


def test_run_subprocess_logs_command(caplog: pytest.LogCaptureFixture) -> None:
    import logging

    with caplog.at_level(logging.DEBUG):
        _ = run_subprocess(["echo", "test"], cwd=Path("/tmp"), check=False, yes=False)
        assert "echo" in caplog.text
        assert "test" in caplog.text
