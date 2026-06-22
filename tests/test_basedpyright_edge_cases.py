from __future__ import annotations

from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from unittest.mock import MagicMock

from pytest import raises

from bygge.contracts import Payload
from bygge.plugins.basedpyright import Basedpyright
from bygge.workspace import Workspace


def test_basedpyright_run_type_check_unexpected_returncode(
    tmp_workspace_dir: Path, tmp_package: Path, mock_subprocess: MagicMock
) -> None:
    """Test Basedpyright run_type_check with unexpected return code."""
    plugin = Basedpyright()
    workspace = Workspace.open(tmp_workspace_dir)
    payload = Payload(
        source_dirs=[tmp_package / "src" / "test_pkg"],
        test_dirs=[tmp_package / "tests"],
    )

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=99, stdout="", stderr="")

    with raises(CalledProcessError):
        _ = plugin.run_type_check(workspace=workspace, payload=payload, args=())
