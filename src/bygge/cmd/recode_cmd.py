from __future__ import annotations

from logging import info, warning
from pathlib import Path

import libcst

from bygge import ByggeError
from bygge.util import RewriteNonAsciiStrings, walk_dir
from bygge.workspace import Workspace

DEFAULT_EXT: str = ".py"


def recode(workspace: Workspace, fix: bool) -> None:
    if fix:
        info("Fixing non-ASCII characters")
    else:
        info("Checking for non-ASCII characters")

    count = 0
    fixed_count = 0

    transformer = RewriteNonAsciiStrings()
    for dir, file_names in walk_dir(start_dir=workspace.workspace_dir):
        for f in file_names:
            count += 1
            p = dir / f
            if p.suffix == DEFAULT_EXT and _transform_file(
                workspace=workspace, transformer=transformer, path=p, fix=fix
            ):
                fixed_count += 1

    info(f"Processed {count} files")

    if fix:
        info(f"Fixed non-ASCII characters in {fixed_count} files")
    elif fixed_count > 0:
        raise ByggeError(f"Detected non-ASCII characters in {fixed_count} files")
    else:
        info("No non-ASCII characters detected")


def _transform_file(
    workspace: Workspace, transformer: RewriteNonAsciiStrings, path: Path, fix: bool
) -> bool:
    rel_path = path.relative_to(workspace.workspace_dir).as_posix()
    s = path.read_text(encoding="utf-8")
    try:
        module = libcst.parse_module(s)
    except Exception as e:  # pragma: no cover
        warning(f"Could not parse {rel_path} ({e})")
        return False

    new_module = module.visit(transformer)
    output = new_module.code
    if output != s:
        if fix:
            _ = path.write_text(output, encoding="utf-8")
            info(f"Fixed non-ASCII characters in {rel_path}")
        else:  # pragma: no cover
            info(f"Found non-ASCII characters in {rel_path}")
        return True
    else:
        return False
