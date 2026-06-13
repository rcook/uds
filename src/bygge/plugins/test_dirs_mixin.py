from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input
from bygge.util import TomlValue, query_toml, try_str_list

from .util import get_requirements


class TestDirsMixin:
    def fetch_test_dirs(self, input: Input, blob: TomlValue) -> list[Path] | None:
        requirements = get_requirements(input=input, blob=blob)
        if not any(map(lambda req: req.name == "pytest", requirements)):
            return None

        node = try_str_list(query_toml(blob, "tool.pytest.ini_options.testpaths"))
        if node is None:
            return None

        return [(input.pyproject_path.parent / s).resolve() for s in node]
