from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input
from bygge.util import TomlValue, query_toml, try_str_list


class Setuptools:
    def fetch_source_dirs(self, input: Input, blob: TomlValue) -> list[Path] | None:
        build_backend = query_toml(blob, "build-system.build-backend")
        if build_backend != "setuptools.build_meta":
            return None

        where = try_str_list(query_toml(blob, "tool.setuptools.packages.find.where"))
        if where is None:
            return None

        return [(input.pyproject_path.parent / d).resolve() for d in where]
