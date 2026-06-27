from __future__ import annotations

from typing import Literal, override

from libcst import CSTTransformer, SimpleString


def to_ascii_escapes(s: str) -> str:
    def escape(c: str) -> str:
        cp = ord(c)
        if cp < 128:
            return c
        elif cp <= 0xFFFF:
            return f"\\u{cp:04x}"
        else:
            return f"\\U{cp:08x}"

    return "".join([escape(c) for c in s])


def detect_quote_style(s: str) -> Literal["'''", '"""', "'", '"']:
    if "'''" in s[:10] or s.lstrip().startswith("'''"):
        return "'''"
    if '"""' in s[:10] or s.lstrip().startswith('"""'):
        return '"""'
    if s.lstrip().startswith("'"):
        return "'"
    return '"'


class RewriteNonAsciiStrings(CSTTransformer):
    @override
    def leave_SimpleString(
        self, original_node: SimpleString, updated_node: SimpleString
    ) -> SimpleString:
        try:
            decoded = original_node.evaluated_value
        except Exception:  # pragma: no cover
            return updated_node

        if not isinstance(decoded, str):  # pragma: no cover
            return updated_node

        if all(ord(c) < 128 for c in decoded):
            return updated_node

        escaped = to_ascii_escapes(decoded)

        token_text = original_node.value
        quote = detect_quote_style(token_text)

        if quote in ("'''", '"""'):
            return SimpleString(f"{quote}{escaped}{quote}")

        return SimpleString(f"{quote}{escaped}{quote}")
