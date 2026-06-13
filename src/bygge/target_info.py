from __future__ import annotations

from dataclasses import dataclass
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Self

from bygge.constants import (
    PYPROJECT_FILE_NAME,
    REQUIREMENTS_PATTERN,
)
from bygge.package_meta import PackageMeta
from bygge.util.fs import walk_dir
from bygge.workspace import Workspace


@dataclass(frozen=True)
class TargetInfo:
    ordered_metas: list[PackageMeta]
    requirements_paths: list[Path]

    @classmethod
    def build(cls: type[Self], workspace: Workspace) -> Self:
        pyproject_paths: list[Path] = []
        requirements_paths: list[Path] = []

        for dir, file_names in walk_dir(workspace.workspace_dir):
            # Check if dir is package_root_dir or a child of it
            if (
                dir == workspace.package_root_dir or workspace.package_root_dir in dir.parents
            ) and PYPROJECT_FILE_NAME in file_names:
                pyproject_paths.append(dir / PYPROJECT_FILE_NAME)

            for file_name in file_names:
                m = REQUIREMENTS_PATTERN.match(file_name)
                if m is None:
                    continue

                names = {
                    s for g in m.groups() if isinstance(g, str) and len(s := g.strip(" -")) > 0
                }
                if len(names) == 0 or len(names.intersection(workspace.optional_deps)) > 0:
                    requirements_paths.append(dir / file_name)

        metas = [
            package
            for p in pyproject_paths
            if (package := PackageMeta.load(p, workspace.optional_deps)) is not None
        ]

        map = {p.name: p for p in metas}
        sorter = TopologicalSorter[str]()
        for package in metas:
            local_requirements = [
                req.name
                for req in package.requirements
                if len(req.specifier) == 0 and req.name in map
            ]
            sorter.add(package.name, *local_requirements)

        sorter.prepare()

        ordered_metas = [map[package_name] for package_name in sorter.static_order()]

        return cls(ordered_metas=ordered_metas, requirements_paths=requirements_paths)
