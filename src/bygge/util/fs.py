from __future__ import annotations

import os
import shlex
import stat
from collections.abc import Generator, Iterable
from fnmatch import fnmatch
from logging import warning
from pathlib import Path

import mslex

from bygge.constants import DOT_FILE_NAME, IGNORE_DIR_GLOBS, IS_WINDOWS

from .assert_never import assert_never
from .unset import UNSET, Unset


def find_dot_file(start_dir: Path) -> Path | None:
    d = start_dir
    while True:
        p = d / DOT_FILE_NAME
        if p.is_file():
            return p

        parent = d.parent
        if parent == d:
            return None

        d = parent


def is_ignored_dir_name(name: str, globs: Iterable[str] | None | Unset = UNSET) -> bool:
    globs0: Iterable[str]
    match globs:
        case Iterable() as c:
            globs0 = c
        case None:
            globs0 = []
        case Unset():
            globs0 = IGNORE_DIR_GLOBS
        case _:  # pragma: nocover  # pyright: ignore[reportUnnecessaryComparison]
            assert_never(globs0)
    return any(fnmatch(name, glob) for glob in globs0)


def walk_dir(
    start_dir: Path, ignore_dir_globs: Iterable[str] | None | Unset = UNSET
) -> Generator[tuple[Path, list[str]]]:

    for dir, dir_names, file_names in start_dir.walk():
        for d in list(dir_names):
            if is_ignored_dir_name(d, ignore_dir_globs):
                dir_names.remove(d)

        yield dir, file_names


def hackily_canonicalize(s: str) -> Path:  # pragma: nocover
    p = Path(s)
    if p.is_file():
        return p

    if not IS_WINDOWS:
        warning(f"Could not find {p}")
        return p

    # Good ol' Windows!

    t0 = os.getenv("PATHEXT")
    if t0 is None:
        warning(f"Could not determine canonical path for {p}")
        return p

    path_exts = [e.lower() for e in t0.split(os.path.pathsep)]
    base_name = p.name.lower()
    for p0 in p.parent.rglob(f"{base_name}*"):
        f = p0.name.lower()
        for path_ext in path_exts:
            if f == base_name + path_ext:
                return p0

    warning(f"Could not determine canonical path for {p}")
    return p


def shell_join(cmd: list[str]) -> str:  # pragma: nocover
    if IS_WINDOWS:
        return mslex.join(split_command=cmd)
    else:
        return shlex.join(split_command=cmd)


def chmod_plus_x(path: Path) -> None:
    st = path.stat()
    mode = st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    path.chmod(mode)
