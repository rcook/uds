from __future__ import annotations

from typing import Protocol

from bygge.workspace import Workspace

from .payload import Payload
from .plugin import Plugin
from .plugin_result import PluginResult


class DeadCodePlugin(Plugin, Protocol):
    def run_dead_code(
        self, workspace: Workspace, payload: Payload, fix: bool, args: tuple[str, ...]
    ) -> PluginResult: ...
