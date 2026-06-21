from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input, Payload, TypeCheckPlugin
from bygge.package_info.context import Context
from bygge.package_info.plugin_info import PluginInfo
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


def test_plugin_info_find_returns_first_installed(tmp_package: Path) -> None:
    """Test PluginInfo.find returns the first installed plugin."""
    plugins = Plugins(
        source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_plugins=[PytestDiscovery()],
        test_plugins=[Pytest()],
        coverage_plugins=[PytestCov()],
        type_check_plugins=[Basedpyright()],
        format_plugins=[RuffFormatPlugin()],
    )
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"])
    blob = load_toml(pyproject_path)
    payload = Payload(source_dirs=[tmp_package / "src"], test_dirs=[tmp_package / "tests"])
    ctx = Context(plugins=plugins, input=input, blob=blob, payload=payload)

    plugin_info = PluginInfo[TypeCheckPlugin].find(ctx=ctx, plugins=plugins.type_check_plugins)

    assert plugin_info is not None
    assert isinstance(plugin_info.plugin, Basedpyright)


def test_plugin_info_find_returns_none_when_no_plugin_installed(tmp_workspace: Path) -> None:
    """Test PluginInfo.find returns None when no plugins are installed."""
    pkg_dir = tmp_workspace / "packages" / "no_plugins"
    pkg_dir.mkdir(parents=True)

    pyproject_path = pkg_dir / "pyproject.toml"
    _ = pyproject_path.write_text('[project]\nname = "no_plugins"\nversion = "0.1.0"\n')

    plugins = Plugins(
        source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_plugins=[PytestDiscovery()],
        test_plugins=[Pytest()],
        coverage_plugins=[PytestCov()],
        type_check_plugins=[Basedpyright()],
        format_plugins=[RuffFormatPlugin()],
    )
    input = Input(pyproject_path=pyproject_path, optional_deps=[])
    blob = load_toml(pyproject_path)
    payload = Payload(source_dirs=[], test_dirs=[])
    ctx = Context(plugins=plugins, input=input, blob=blob, payload=payload)

    plugin_info = PluginInfo[TypeCheckPlugin].find(ctx=ctx, plugins=plugins.type_check_plugins)

    assert plugin_info is None
