from __future__ import annotations

from .basedpyright import Basedpyright
from .hatchling import Hatchling
from .magic_sources import MagicSources
from .magic_tests import MagicTests
from .plugins import Plugins
from .pytest import Pytest
from .pytest_cov import PytestCov
from .pytest_discovery import PytestDiscovery
from .ruff_check_plugin import RuffCheckPlugin
from .ruff_format_plugin import RuffFormatPlugin
from .setuptools import Setuptools

__all__ = [
    "Basedpyright",
    "Hatchling",
    "MagicSources",
    "MagicTests",
    "Plugins",
    "Pytest",
    "PytestCov",
    "PytestDiscovery",
    "RuffCheckPlugin",
    "RuffFormatPlugin",
    "Setuptools",
]
