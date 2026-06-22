from __future__ import annotations

from pathlib import Path

from bygge.constants import DOT_FILE_NAME
from bygge.workspace import Workspace


def test_workspace_probe_no_workspace(tmp_path: Path) -> None:
    assert Workspace.probe(cwd=tmp_path, workspace_dir=None) is None


def test_workspace_probe_workspace(tmp_path: Path) -> None:
    (tmp_path / DOT_FILE_NAME).touch()
    assert Workspace.probe(cwd=tmp_path, workspace_dir=None) == tmp_path
