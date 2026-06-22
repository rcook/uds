"""Test that the py.typed marker file exists."""

from __future__ import annotations

from pathlib import Path


def test_py_typed_marker_exists() -> None:
    """Test that py.typed marker file exists in the package."""
    # Get the path to the bygge package source
    package_dir = Path(__file__).parent.parent / "src" / "bygge"
    py_typed_file = package_dir / "py.typed"

    # The file must exist for type checkers to recognize this as a typed package
    assert py_typed_file.exists(), "py.typed marker file is missing"

    # The file should be empty (standard practice for py.typed markers)
    assert py_typed_file.read_text() == "", "py.typed should be an empty file"
