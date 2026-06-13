from __future__ import annotations

import os
from collections.abc import Generator, Iterable
from logging import warning
from pathlib import Path

from bygge.constants import DOT_FILE_NAME, IGNORE_DIR_NAMES, IS_WINDOWS

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


def walk_dir(
    start_dir: Path, ignore_dir_names: Iterable[str] | None | Unset = UNSET
) -> Generator[tuple[Path, list[str]]]:
    ignore_dir_names0: Iterable[str]
    match ignore_dir_names:
        case Iterable() as c:
            ignore_dir_names0 = c
        case None:
            ignore_dir_names0 = []
        case Unset():
            ignore_dir_names0 = IGNORE_DIR_NAMES
        case _:  # pragma: nocover
            assert_never(ignore_dir_names)

    for dir, dir_names, file_names in start_dir.walk():
        for d in ignore_dir_names0:
            if d in dir_names:
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
