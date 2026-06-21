from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from logging import debug
from typing import Self

from bygge.contracts import Payload, Plugin

from .context import Context


@dataclass(frozen=True, slots=True)
class PluginInfo[P: Plugin]:
    plugin: P
    payload: Payload

    @classmethod
    def find(cls: type[Self], ctx: Context, plugins: Iterable[P]) -> Self | None:
        first_installed = None
        for plugin in plugins:
            is_installed = plugin.is_installed(input=ctx.input, blob=ctx.blob)
            debug(f"Plugin {type(plugin).__name__}: is_installed={is_installed}")
            if is_installed and first_installed is None:
                first_installed = plugin
        return None if first_installed is None else cls(plugin=first_installed, payload=ctx.payload)
