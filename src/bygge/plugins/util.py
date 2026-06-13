from __future__ import annotations

from pathlib import Path

from packaging.requirements import Requirement

from bygge.contracts import Input
from bygge.util import TomlValue, query_toml, try_dict, try_str_list


def get_requirements(input: Input, blob: TomlValue) -> set[Requirement]:
    deps = try_str_list(query_toml(blob, "project.dependencies"))
    requirements = {Requirement(s) for s in deps or []}
    node = try_dict(query_toml(blob, "project.optional-dependencies"))
    if node is not None:
        for optional_dep in input.optional_deps:
            other_deps = try_str_list(node.get(optional_dep))
            if other_deps is not None:
                requirements.update(Requirement(s) for s in other_deps)
    return requirements


def fetch_pytest_test_dirs(
    input: Input, blob: TomlValue, required_deps: list[str]
) -> list[Path] | None:
    requirements = get_requirements(input=input, blob=blob)
    for d in required_deps:
        if not any(map(lambda req: req.name == d, requirements)):
            return None

    node = try_str_list(query_toml(blob, "tool.pytest.ini_options.testpaths"))
    if node is None:
        return None

    return [(input.pyproject_path.parent / s).resolve() for s in node]
