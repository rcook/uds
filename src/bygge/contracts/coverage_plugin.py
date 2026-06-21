from __future__ import annotations

from typing import Protocol

from bygge.workspace import Workspace

from .payload import Payload
from .plugin import Plugin
from .plugin_result import PluginResult


class CoveragePlugin(Plugin, Protocol):
    def run_coverage(
        self,
        workspace: Workspace,
        payload: Payload,
        args: tuple[str, ...],
        coverage_baseline: int | None,
    ) -> PluginResult: ...
