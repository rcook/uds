from __future__ import annotations

from click.testing import CliRunner

from bygge.main import main


def test_main_runs() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
