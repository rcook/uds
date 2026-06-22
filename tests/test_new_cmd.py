from __future__ import annotations

from pathlib import Path

from pytest import raises

from bygge import ByggeError
from bygge.cmd import new
from bygge.constants import DOT_FILE_NAME


def test_new_no_dot_file(tmp_path: Path) -> None:
    dot_path = tmp_path / DOT_FILE_NAME
    assert not dot_path.exists()
    new(workspace_dir=tmp_path)
    assert dot_path.exists()


def test_new_existing_dot_file(tmp_path: Path) -> None:
    dot_path = tmp_path / DOT_FILE_NAME
    dot_path.touch()
    with raises(ByggeError, match=r"^Target path .+ already exists$"):
        new(workspace_dir=tmp_path)
