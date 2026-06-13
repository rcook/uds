from __future__ import annotations

from dataclasses import dataclass

from bygge.contracts import Input, Payload
from bygge.plugins import Plugins
from bygge.util import TomlValue


@dataclass(frozen=True)
class Context:
    plugins: Plugins
    input: Input
    blob: TomlValue
    payload: Payload
