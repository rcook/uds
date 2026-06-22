from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input
from bygge.package_info.package_info import SkinnyContext
from bygge.plugins import (
    Basedpyright,
    Hatchling,
    MagicSources,
    Plugins,
    Pytest,
    PytestCov,
    PytestDiscovery,
    RuffFormatPlugin,
    Setuptools,
)
from bygge.util import load_toml


def test_package_info_get_test_dirs_none_found(tmp_workspace_dir: Path) -> None:
    """Test PackageInfo._get_test_dirs returns None when no tools find test dirs."""
    # Create a package without pytest in dependencies and no testpaths config
    pkg_dir = tmp_workspace_dir / "packages" / "no_tests"
    pkg_dir.mkdir(parents=True)

    pyproject_path = pkg_dir / "pyproject.toml"
    _ = pyproject_path.write_text(
        "[build-system]\n"
        + 'requires = ["hatchling"]\n'
        + 'build-backend = "hatchling.build"\n'
        + "\n"
        + "[project]\n"
        + 'name = "no_tests"\n'
        + 'version = "0.1.0"\n'
        + "dependencies = []\n"
    )

    plugins = Plugins(
        source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_plugins=[PytestDiscovery()],
        test_plugins=[Pytest()],
        coverage_plugins=[PytestCov()],
        type_check_plugins=[Basedpyright()],
        format_plugins=[RuffFormatPlugin()],
    )
    blob = load_toml(pyproject_path)
    skinny_ctx = SkinnyContext(
        plugins=plugins,
        input=Input(pyproject_path=pyproject_path, optional_deps=[]),
        blob=blob,
    )

    test_dirs = skinny_ctx.get_test_dirs()

    assert test_dirs is None
