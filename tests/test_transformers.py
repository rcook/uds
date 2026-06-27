from __future__ import annotations

from pytest import mark

from bygge.util.transformers import detect_quote_style, to_ascii_escapes


@mark.parametrize(
    "input, expected",
    [
        ("hello", "hello"),
        ("shake hands with " + chr(0xBEEF), "shake hands with \\ubeef"),
        ("goodbye " + chr(0x10FFFF), "goodbye \\U0010ffff"),
    ],
)
def test_to_ascii_escapes(input: str, expected: str) -> None:
    assert to_ascii_escapes(input) == expected


@mark.parametrize(
    "input, expected",
    [("x", '"'), ('   """x"""', '"""'), ("   '''x'''", "'''"), ('"x"', '"'), ("'x'", "'")],
)
def test_detect_quote_style(input: str, expected: str) -> None:
    assert detect_quote_style(input) == expected
