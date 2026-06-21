from __future__ import annotations

from enum import Enum, auto, unique


@unique
class PluginResult(Enum):
    PASSED = auto()
    FAILED = auto()
    PLUGIN_ERROR = auto()
