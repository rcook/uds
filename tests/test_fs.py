from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path
from unittest.mock import patch

from bygge.constants import DOT_FILE_NAME, IS_WINDOWS
from bygge.util import UNSET, Unset
from bygge.util.fs import find_dot_file, hackily_canonicalize, walk_dir


def test_find_dot_file_in_current_dir(tmp_path: Path) -> None:
    dot_path = tmp_path / DOT_FILE_NAME
    dot_path.touch()
    assert find_dot_file(tmp_path) == dot_path


def test_find_dot_file_in_parent(tmp_path: Path) -> None:
    dot_path = tmp_path / DOT_FILE_NAME
    dot_path.touch()
    subdir = tmp_path / "sub" / "dir"
    subdir.mkdir(parents=True)
    assert find_dot_file(subdir) == dot_path


def test_find_dot_file_not_found(tmp_path: Path) -> None:
    assert find_dot_file(tmp_path) is None


def test_find_dot_file_stops_at_root(tmp_path: Path) -> None:
    # If we reach the filesystem root without finding the file, return None
    deep_dir = tmp_path / "a" / "b" / "c" / "d"
    deep_dir.mkdir(parents=True)
    assert find_dot_file(deep_dir) is None


def test_walk_dir_basics(tmp_path: Path) -> None:
    def make_file(path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text("")

    def run_walk_dir(
        start_dir: Path, ignore_dir_names: Iterable[str] | None | Unset = UNSET
    ) -> list[str]:
        paths: list[str] = []
        for dir, file_names in walk_dir(start_dir=start_dir, ignore_dir_globs=ignore_dir_names):
            for f in file_names:
                paths.append((dir / f).relative_to(tmp_path).as_posix())
        return sorted(paths)

    make_file(tmp_path / "a" / "b" / "c")
    make_file(tmp_path / "a" / "b" / "d")
    make_file(tmp_path / "a" / "b" / "e")
    make_file(tmp_path / ".venv" / "f" / "g")

    paths = run_walk_dir(tmp_path)
    assert paths == sorted(["a/b/c", "a/b/d", "a/b/e"])

    paths = run_walk_dir(tmp_path, ignore_dir_names=None)
    assert paths == sorted([".venv/f/g", "a/b/c", "a/b/d", "a/b/e"])

    paths = run_walk_dir(tmp_path, ignore_dir_names=["b"])
    assert paths == sorted([".venv/f/g"])


def test_walk_dir_consecutive_ignored_dirs(tmp_path: Path) -> None:
    """Test that consecutive ignored directories are both pruned correctly."""
    (tmp_path / ".git" / "objects").mkdir(parents=True)
    _ = (tmp_path / ".git" / "file1.txt").write_text("")
    (tmp_path / ".venv" / "lib").mkdir(parents=True)
    _ = (tmp_path / ".venv" / "file2.txt").write_text("")
    (tmp_path / "src").mkdir(parents=True)
    _ = (tmp_path / "src" / "file3.txt").write_text("")

    paths: list[str] = []
    for dir, file_names in walk_dir(start_dir=tmp_path):
        for f in file_names:
            paths.append((dir / f).relative_to(tmp_path).as_posix())

    # Only src/file3.txt should be found; .git and .venv are ignored by default
    assert sorted(paths) == ["src/file3.txt"]


def test_hackily_canonicalize(tmp_path: Path) -> None:
    file_name = "foo.cmd" if IS_WINDOWS else "foo"
    bin_path = tmp_path / file_name
    _ = bin_path.write_text("")

    # Full path resolves to full path of existing file
    assert hackily_canonicalize(str(bin_path)) == bin_path

    with patch.dict(os.environ, clear=True):
        p = bin_path.parent / "nonexistent"
        assert hackily_canonicalize(str(p)) == p

    # File path with no extension, finds first executable file that matches
    assert hackily_canonicalize(str(bin_path.parent / bin_path.stem)) == bin_path
