from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from bygge import ByggeError
from bygge.constants import DOT_FILE_NAME, IS_WINDOWS
from bygge.dot_config import DotConfig
from bygge.util import find_dot_file


@dataclass(frozen=True)
class Workspace:
    cwd: Path
    workspace_dir: Path
    package_root_dir: Path
    venv_dir: Path
    optional_deps: list[str]
    coverage_baseline: int | None

    @staticmethod
    def probe(cwd: Path, workspace_dir: Path | None) -> Path | None:
        if workspace_dir is None:
            dot_path = find_dot_file(cwd)
            if dot_path is None:
                return None
        else:
            dot_path = workspace_dir / DOT_FILE_NAME
            if not dot_path.is_file():
                return None

        return dot_path.parent

    @classmethod
    def open(cls: type[Self], workspace_dir: Path, cwd: Path | None = None) -> Self:
        dot_path = workspace_dir / DOT_FILE_NAME
        dot_config = DotConfig.load(workspace_dir=workspace_dir, dot_path=dot_path)
        # package_root_dir can be equal to or a child of workspace_dir
        assert (
            workspace_dir == dot_config.package_root_dir
            or workspace_dir in dot_config.package_root_dir.parents
        )

        return cls(
            cwd=cwd or workspace_dir,
            workspace_dir=workspace_dir,
            package_root_dir=dot_config.package_root_dir,
            venv_dir=dot_config.venv_dir,
            optional_deps=dot_config.optional_deps,
            coverage_baseline=dot_config.coverage_baseline,
        )

    def make_bin_path(self, name: str, must_exist: bool = True) -> Path:
        p = (
            self.venv_dir / "Scripts" / f"{name}.exe"
            if IS_WINDOWS
            else self.venv_dir / "bin" / name
        )

        if must_exist and not p.is_file():
            raise ByggeError(f"Cannot find binary {p}")

        return p
