from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from logging import debug
from typing import Self

from bygge.contracts import Payload, Tool

from .context import Context


@dataclass(frozen=True, slots=True)
class ToolInfo[T: Tool]:
    tool: T
    payload: Payload

    @classmethod
    def find(cls: type[Self], ctx: Context, tools: Iterable[T]) -> Self | None:
        first_installed = None
        for tool in tools:
            is_installed = tool.is_installed(input=ctx.input, blob=ctx.blob)
            debug(f"Plugin {type(tool).__name__}: is_installed={is_installed}")
            if is_installed and first_installed is None:
                first_installed = tool
        return None if first_installed is None else cls(tool=first_installed, payload=ctx.payload)
