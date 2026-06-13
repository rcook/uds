from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input
from bygge.plugins.setuptools import Setuptools
from bygge.util import load_toml


def test_setuptools_missing_where(tmp_workspace: Path) -> None:
    """Test Setuptools plugin returns None when where is missing."""
    plugin = Setuptools()
    pkg_dir = tmp_workspace / "packages" / "setuptools_no_where"
    pkg_dir.mkdir(parents=True)

    pyproject_path = pkg_dir / "pyproject.toml"
    _ = pyproject_path.write_text(
        "[build-system]\n"
        + 'requires = ["setuptools"]\n'
        + 'build-backend = "setuptools.build_meta"\n'
        + "\n"
        + "[project]\n"
        + 'name = "test"\n'
        + 'version = "0.1.0"\n'
    )

    input = Input(pyproject_path=pyproject_path, optional_deps=[])
    blob = load_toml(pyproject_path)

    source_dirs = plugin.fetch_source_dirs(input=input, blob=blob)
    assert source_dirs is None
