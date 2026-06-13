from __future__ import annotations

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

PLUGINS: Plugins = Plugins(
    source_dir_tools=[Hatchling(), Setuptools(), MagicSources()],
    test_dir_tools=[PytestDiscovery()],
    test_tools=[Pytest()],
    coverage_tools=[PytestCov()],
    type_check_tools=[Basedpyright()],
)
