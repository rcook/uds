from __future__ import annotations

from typing import cast

from bygge.util import TomlValue, query_toml, try_str_list


class TestToml:
    def test_empty_query(self) -> None:
        obj = cast(TomlValue, {"section0": {"key0": "value0"}})
        assert query_toml(obj, "") == obj
        assert query_toml(obj, " ") == obj
        assert query_toml(obj, "section0") == {"key0": "value0"}
        assert query_toml(obj, "section0.key0") == "value0"
        assert query_toml("value0", "") == "value0"
        assert query_toml("value0", "key0") is None
        assert query_toml("value0", "section0.key0") is None

    def test_try_str_list(self) -> None:
        assert try_str_list(["a", "b"]) == ["a", "b"]
        assert try_str_list([1, 2]) is None
        assert try_str_list("not a list") is None
        assert try_str_list(["a", 1]) is None
