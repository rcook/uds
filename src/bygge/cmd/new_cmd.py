from __future__ import annotations

import shutil
from logging import info
from pathlib import Path

from bygge import ByggeError
from bygge.constants import DOT_FILE_NAME

_DOT_FILE_TEMPLATE: Path = Path(__file__).parents[1] / "resources" / "bygge-template.txt"


def new(workspace_dir: Path) -> None:
    target_path = workspace_dir / DOT_FILE_NAME
    if target_path.exists():
        raise ByggeError(f"Target path {target_path} already exists")

    _ = shutil.copyfile(_DOT_FILE_TEMPLATE, target_path)
    info(f"Created bygge workspace configuration file at {target_path}")
