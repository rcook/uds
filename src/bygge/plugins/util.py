from __future__ import annotations

from pathlib import Path

from packaging.requirements import Requirement

from bygge.contracts import Input
from bygge.requirements import get_requirements as _get_requirements
from bygge.util import TomlValue, query_toml, try_str_list


def get_requirements(input: Input, blob: TomlValue) -> set[Requirement]:
    return _get_requirements(blob=blob, optional_deps=input.optional_deps)


def check_requirements(input: Input, blob: TomlValue, required_deps: list[str]) -> bool:
    requirements = get_requirements(input=input, blob=blob)
    return all(any(map(lambda req: req.name == d, requirements)) for d in required_deps)


def fetch_pytest_test_dirs(input: Input, blob: TomlValue) -> list[Path] | None:
    node = try_str_list(query_toml(blob, "tool.pytest.ini_options.testpaths"))
    if node is None:
        return None

    return [(input.pyproject_path.parent / s).resolve() for s in node]
