from __future__ import annotations

from dataclasses import dataclass
from logging import warning
from pathlib import Path
from typing import Self

from packaging.requirements import Requirement

from bygge.requirements import get_requirements
from bygge.util import (
    TomlValue,
    load_toml,
    query_toml,
    try_dict,
    try_str,
    try_str_list,
)


@dataclass(frozen=True)
class PackageMeta:
    blob: TomlValue
    name: str
    pyproject_path: Path
    package_dir: Path
    requirements: set[Requirement]
    build_backend: str
    build_requires: list[str]

    @classmethod
    def load(cls: type[Self], pyproject_path: Path, optional_deps: list[str]) -> Self | None:
        obj = try_dict(load_toml(pyproject_path))
        if obj is None:  # pragma: no cover - TOML root is always a dict
            warning(f"Invalid project file {pyproject_path}")
            return None

        blob = obj

        name = query_toml(blob, "project.name")
        if not isinstance(name, str):
            return None

        requirements = get_requirements(blob=blob, optional_deps=optional_deps)

        build_backend = try_str(query_toml(blob, "build-system.build-backend"))
        if build_backend is None:
            warning(f"Project file {pyproject_path} does not specify build backend")
            return None

        build_requires = try_str_list(query_toml(blob, "build-system.requires")) or []

        return cls(
            blob=obj,
            name=name,
            pyproject_path=pyproject_path,
            package_dir=pyproject_path.parent,
            requirements=requirements,
            build_backend=build_backend,
            build_requires=build_requires,
        )
