"""Test TOML error handling provides user-friendly messages."""

from __future__ import annotations

from pathlib import Path

from pytest import raises

from bygge import ByggeError
from bygge.util import load_toml


def test_load_toml_malformed_syntax(tmp_path: Path) -> None:
    """Test that malformed TOML raises ByggeError with helpful message."""
    toml_path = tmp_path / "bad.toml"
    _ = toml_path.write_text("invalid syntax [[[")

    with raises(ByggeError) as exc_info:
        _ = load_toml(toml_path)

    # Error message should include the file path and parsing error
    error_msg = str(exc_info.value)
    assert "bad.toml" in error_msg
    assert "Error parsing" in error_msg


def test_load_toml_missing_equals(tmp_path: Path) -> None:
    """Test that TOML with missing = raises ByggeError."""
    toml_path = tmp_path / "missing_equals.toml"
    _ = toml_path.write_text("[section]\nkey value")

    with raises(ByggeError) as exc_info:
        _ = load_toml(toml_path)

    # Error message should include the file path
    error_msg = str(exc_info.value)
    assert "missing_equals.toml" in error_msg
    assert "Error parsing" in error_msg


def test_load_toml_valid_file(tmp_path: Path) -> None:
    """Test that valid TOML loads successfully."""
    toml_path = tmp_path / "good.toml"
    _ = toml_path.write_text('[section]\nkey = "value"\n')

    # Should not raise any exception
    result = load_toml(toml_path)

    assert isinstance(result, dict)
    assert "section" in result
