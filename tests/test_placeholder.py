from __future__ import annotations

from click.testing import CliRunner

from bygge import VERSION
from bygge.main import main


def test_version() -> None:
    assert VERSION == "0.1.0"


def test_main_runs() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
