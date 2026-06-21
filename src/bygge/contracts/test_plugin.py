from __future__ import annotations

from typing import Protocol

from bygge.workspace import Workspace

from .payload import Payload
from .plugin import Plugin
from .plugin_result import PluginResult


class TestPlugin(Plugin, Protocol):
    def run_test(
        self,
        workspace: Workspace,
        payload: Payload,
        args: tuple[str, ...],
    ) -> PluginResult: ...
