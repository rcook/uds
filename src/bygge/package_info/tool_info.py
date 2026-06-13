from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

from bygge.contracts import Payload, Tool

from .context import Context


@dataclass(frozen=True, slots=True)
class ToolInfo[T: Tool]:
    tool: T
    payload: Payload

    @classmethod
    def find(cls: type[Self], ctx: Context, tools: Iterable[T]) -> Self | None:
        for tool in tools:
            if tool.is_installed(input=ctx.input, blob=ctx.blob):
                return cls(tool=tool, payload=ctx.payload)
        return None
