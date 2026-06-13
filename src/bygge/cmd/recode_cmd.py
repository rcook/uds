from __future__ import annotations

from logging import debug, info, warning
from pathlib import Path

import libcst

from bygge.util import RewriteNonAsciiStrings, walk_dir

DEFAULT_EXT: str = ".py"


def recode(path: Path, suffix: str | None = None) -> None:
    transformer = RewriteNonAsciiStrings()

    if path.is_file():
        _transform_file(transformer=transformer, path=path)
    elif path.is_dir():
        suffix0 = suffix or DEFAULT_EXT
        for dir, file_names in walk_dir(start_dir=path):
            for f in file_names:
                p = dir / f
                if p.suffix == suffix0:
                    print(f"PROCESSING {p}")
                    _transform_file(transformer=transformer, path=p)
    else:  # pragma: nocover
        raise AssertionError()


def _transform_file(transformer: RewriteNonAsciiStrings, path: Path) -> None:
    debug(f"Checking {path}")

    s = path.read_text(encoding="utf-8")
    try:
        module = libcst.parse_module(s)
    except Exception as e:  # pragma: nocover
        warning(f"Could not parse {path} ({e})")
        return

    new_module = module.visit(transformer)
    output = new_module.code
    if output != s:
        _ = path.write_text(output, encoding="utf-8")
        info(f"updated {path}")
