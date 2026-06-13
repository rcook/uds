from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from bygge import ByggeError
from bygge.constants import VENV_DIR_NAME
from bygge.util import load_toml, query_toml, try_int, try_str, try_str_list


@dataclass(frozen=True)
class DotConfig:
    package_root_dir: Path
    venv_dir: Path
    optional_deps: list[str]
    coverage_baseline: int | None

    @classmethod
    def load(cls: type[Self], workspace_dir: Path, dot_path: Path) -> Self:
        obj = load_toml(dot_path)

        package_root_dir_node = try_str(query_toml(obj, "workspace.package_root_dir"))
        if package_root_dir_node is None:
            package_root_dir = workspace_dir
        else:
            package_root_dir = (workspace_dir / package_root_dir_node).resolve()

        venv_dir_node = try_str(query_toml(obj, "workspace.venv_dir"))
        if venv_dir_node is None:
            venv_dir = workspace_dir / VENV_DIR_NAME
        else:
            venv_dir = (workspace_dir / venv_dir_node).resolve()

        optional_deps = try_str_list(query_toml(obj, "workspace.optional_deps")) or []

        coverage_baseline_node = query_toml(obj, "workspace.coverage_baseline")
        if coverage_baseline_node is None:
            coverage_baseline = None
        else:
            coverage_baseline = try_int(coverage_baseline_node)
            if coverage_baseline is None:
                raise ByggeError(
                    f"Invalid code coverage baseline {coverage_baseline_node} in {dot_path}"
                )

        return cls(
            package_root_dir=package_root_dir,
            venv_dir=venv_dir,
            optional_deps=optional_deps,
            coverage_baseline=coverage_baseline,
        )
