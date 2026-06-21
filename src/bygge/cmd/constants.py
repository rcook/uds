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
    source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
    test_dir_plugins=[PytestDiscovery()],
    test_plugins=[Pytest()],
    coverage_plugins=[PytestCov()],
    type_check_plugins=[Basedpyright()],
)
