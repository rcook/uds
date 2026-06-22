"""Test that PackageInfo.make doesn't re-read pyproject.toml."""

from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input
from bygge.package_info import PackageInfo
from bygge.plugins import Plugins
from bygge.plugins.basedpyright import Basedpyright
from bygge.plugins.hatchling import Hatchling
from bygge.plugins.magic_sources import MagicSources
from bygge.plugins.pytest import Pytest
from bygge.plugins.pytest_cov import PytestCov
from bygge.plugins.pytest_discovery import PytestDiscovery
from bygge.plugins.ruff_check_plugin import RuffCheckPlugin
from bygge.plugins.ruff_format_plugin import RuffFormatPlugin
from bygge.plugins.setuptools import Setuptools
from bygge.util import load_toml


def test_package_info_make_does_not_reread_toml(tmp_package: Path) -> None:
    """Test that PackageInfo.make uses the blob from Input instead of re-reading."""
    plugins = Plugins(
        source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_plugins=[PytestDiscovery()],
        test_plugins=[Pytest()],
        coverage_plugins=[PytestCov()],
        type_check_plugins=[Basedpyright()],
        format_plugins=[RuffFormatPlugin()],
        lint_plugins=[RuffCheckPlugin()],
    )

    pyproject_path = tmp_package / "pyproject.toml"
    blob = load_toml(pyproject_path)
    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"], blob=blob)

    # Delete the file after loading to prove PackageInfo.make doesn't re-read it
    pyproject_path.unlink()

    # PackageInfo.make should still work because it uses the cached blob
    info = PackageInfo.make(plugins=plugins, input=input)

    # The PackageInfo should be created successfully despite the file being deleted
    assert info is not None
    assert info.name == "test_pkg"
