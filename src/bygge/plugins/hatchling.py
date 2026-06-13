from __future__ import annotations

from logging import warning
from pathlib import Path

from bygge.contracts import Input
from bygge.util import TomlValue, query_toml, try_str, try_str_list


class Hatchling:
    def fetch_source_dirs(self, input: Input, blob: TomlValue) -> list[Path] | None:
        build_backend = try_str(query_toml(blob, "build-system.build-backend"))
        if build_backend != "hatchling.build":
            return None

        node = try_str_list(obj=query_toml(blob, "tool.hatch.build.targets.wheel.packages"))
        if node is None:
            warning(f"Hatchling build in {input.pyproject_path} defines no source files")
            return None

        return sorted((input.pyproject_path.parent / s).resolve() for s in node)
