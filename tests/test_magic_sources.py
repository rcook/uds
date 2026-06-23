from __future__ import annotations

from pathlib import Path
from typing import cast

from bygge.contracts import Input
from bygge.plugins import MagicSources
from bygge.util import TomlValue


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True)
    path.touch()


def test_magic_sources_basics(tmp_path: Path) -> None:
    blob = cast(TomlValue, {})
    input = Input(pyproject_path=tmp_path / "pyproject.toml", optional_deps=[], blob=blob)

    module_a = tmp_path / "module_a"
    module_c = tmp_path / "module_c"
    _touch(tmp_path / "test" / "__init__.py")
    _touch(tmp_path / "tests" / "__init__.py")
    _touch(module_a / "__init__.py")
    _touch(tmp_path / "module_a" / "module_b" / "__init__.py")
    _touch(module_c / "__init__.py")

    plugin = MagicSources()
    result = plugin.fetch_source_dirs(input=input, blob=blob)

    assert result == [module_a, module_c]
