from __future__ import annotations

from pathlib import PurePosixPath

from pytest import mark

from bygge.plugins.algorithms import remove_redundant_prefixes, remove_redundant_prefixes_str


@mark.parametrize(
    "inputs, expected",
    [
        ({"ABCD", "ABC"}, {"ABC"}),
        ({"ABCD", "ABC", "DEF", "D"}, {"ABC", "D"}),
        ({"AB", "ABC", "ABX"}, {"AB"}),
        ({"A", "AB", "C"}, {"A", "C"}),
        ({"XYZA", "XYZAB", "XYZC"}, {"XYZA", "XYZC"}),
    ],
)
def test_remove_redundant_prefixes(inputs: set[str], expected: set[str]) -> None:
    assert remove_redundant_prefixes_str(inputs) == expected
    inputs0 = {PurePosixPath(*input).parts for input in inputs}
    result = remove_redundant_prefixes(inputs0)
    assert {PurePosixPath(*parts) for parts in result} == {PurePosixPath(*s) for s in expected}
