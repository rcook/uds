from __future__ import annotations

from logging import LogRecord

from bygge.util.colour_formatter import ColourFormatter


def test_colour_formatter_info() -> None:
    formatter = ColourFormatter("[%(levelname)s] %(message)s")
    record = LogRecord(
        name="test",
        level=20,  # INFO
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    result = formatter.format(record)
    assert "INFO" in result
    assert "Test message" in result


def test_colour_formatter_warning() -> None:
    formatter = ColourFormatter("[%(levelname)s] %(message)s")
    record = LogRecord(
        name="test",
        level=30,  # WARNING
        pathname="",
        lineno=0,
        msg="Warning message",
        args=(),
        exc_info=None,
    )
    result = formatter.format(record)
    assert "WARNING" in result


def test_colour_formatter_error() -> None:
    formatter = ColourFormatter("[%(levelname)s] %(message)s")
    record = LogRecord(
        name="test",
        level=40,  # ERROR
        pathname="",
        lineno=0,
        msg="Error message",
        args=(),
        exc_info=None,
    )
    result = formatter.format(record)
    assert "ERROR" in result


def test_colour_formatter_debug() -> None:
    formatter = ColourFormatter("[%(levelname)s] %(message)s")
    record = LogRecord(
        name="test",
        level=10,  # DEBUG
        pathname="",
        lineno=0,
        msg="Debug message",
        args=(),
        exc_info=None,
    )
    result = formatter.format(record)
    assert "DEBUG" in result


def test_colour_formatter_unknown_level() -> None:
    formatter = ColourFormatter("[%(levelname)s] %(message)s")
    record = LogRecord(
        name="test",
        level=99,  # Unknown
        pathname="",
        lineno=0,
        msg="Unknown message",
        args=(),
        exc_info=None,
    )
    record.levelname = "CUSTOM"
    result = formatter.format(record)
    assert "CUSTOM" in result
    assert "Unknown message" in result
