from __future__ import annotations

type JsonPrimitive = None | bool | int | float | str
type JsonDict = dict[str, JsonValue]
type JsonList = list[JsonValue]
type JsonValue = JsonPrimitive | JsonDict | JsonList
