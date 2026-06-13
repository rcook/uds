from __future__ import annotations

from packaging.requirements import Requirement

from bygge.util import (
    TomlValue,
    query_toml,
    try_dict,
    try_str_list,
)


def get_requirements(blob: TomlValue, optional_deps: list[str]) -> set[Requirement]:
    deps = try_str_list(query_toml(blob, "project.dependencies"))
    requirements = {Requirement(s) for s in deps or []}
    node = try_dict(query_toml(blob, "project.optional-dependencies"))
    if node is not None:
        for optional_dep in optional_deps:
            t0 = try_str_list(node.get(optional_dep))
            if t0 is not None:
                requirements.update(Requirement(s) for s in t0)
    return requirements
