from __future__ import annotations

import tomllib
from datetime import datetime
from pathlib import Path
from typing import cast

type TomlPrimitive = str | int | float | bool | datetime
type TomlList = list[TomlValue]
type TomlDict = dict[str, TomlValue]
type TomlValue = TomlPrimitive | TomlList | TomlDict


def load_toml(path: Path) -> TomlValue:
    return cast(TomlValue, tomllib.loads(path.read_text()))


def query_toml(obj: TomlValue, q: str) -> TomlValue | None:
    parts = [p.strip() for p in q.split(".")]
    if parts == [""]:
        return obj

    path = parts[:-1]
    leaf = parts[-1]

    node = try_dict(obj)
    if node is None:
        return None

    for key in path:
        next_node = try_dict(node.get(key))
        if next_node is None:
            return None
        node = next_node

    return node.get(leaf)


def try_dict(obj: TomlValue | None) -> TomlDict | None:
    return obj if isinstance(obj, dict) else None


def try_int(obj: TomlValue | None) -> int | None:
    return obj if isinstance(obj, int) else None


def try_str(obj: TomlValue | None) -> str | None:
    return obj if isinstance(obj, str) else None


def try_str_list(obj: TomlValue | None) -> list[str] | None:
    if not isinstance(obj, list):
        return None

    if not all(map(lambda node: isinstance(node, str), obj)):
        return None

    return cast(list[str], obj)
