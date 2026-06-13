from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input, Payload, TypeCheckTool
from bygge.package_info.context import Context
from bygge.package_info.tool_info import ToolInfo
from bygge.plugins import (
    Basedpyright,
    Hatchling,
    MagicSources,
    Plugins,
    Pytest,
    PytestCov,
    PytestDiscovery,
    Setuptools,
)
from bygge.util import load_toml


def test_tool_info_find_returns_first_installed(tmp_package: Path) -> None:
    """Test ToolInfo.find returns the first installed tool."""
    plugins = Plugins(
        source_dir_tools=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_tools=[PytestDiscovery()],
        test_tools=[Pytest()],
        coverage_tools=[PytestCov()],
        type_check_tools=[Basedpyright()],
    )
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"])
    blob = load_toml(pyproject_path)
    payload = Payload(source_dirs=[tmp_package / "src"], test_dirs=[tmp_package / "tests"])
    ctx = Context(plugins=plugins, input=input, blob=blob, payload=payload)

    tool_info = ToolInfo[TypeCheckTool].find(ctx=ctx, tools=plugins.type_check_tools)

    assert tool_info is not None
    assert isinstance(tool_info.tool, Basedpyright)


def test_tool_info_find_returns_none_when_no_tool_installed(tmp_workspace: Path) -> None:
    """Test ToolInfo.find returns None when no tools are installed."""
    pkg_dir = tmp_workspace / "packages" / "no_tools"
    pkg_dir.mkdir(parents=True)

    pyproject_path = pkg_dir / "pyproject.toml"
    _ = pyproject_path.write_text('[project]\nname = "no_tools"\nversion = "0.1.0"\n')

    plugins = Plugins(
        source_dir_tools=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_tools=[PytestDiscovery()],
        test_tools=[Pytest()],
        coverage_tools=[PytestCov()],
        type_check_tools=[Basedpyright()],
    )
    input = Input(pyproject_path=pyproject_path, optional_deps=[])
    blob = load_toml(pyproject_path)
    payload = Payload(source_dirs=[], test_dirs=[])
    ctx = Context(plugins=plugins, input=input, blob=blob, payload=payload)

    tool_info = ToolInfo[TypeCheckTool].find(ctx=ctx, tools=plugins.type_check_tools)

    assert tool_info is None
