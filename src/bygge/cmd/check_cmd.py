from __future__ import annotations

import click

from bygge.workspace import Workspace

from .coverage_cmd import coverage
from .fmt_cmd import fmt
from .lint_cmd import lint
from .type_check_cmd import type_check


def check(workspace: Workspace) -> None:
    click.echo("Checking formatting...")
    fmt(workspace=workspace, fix=False)
    click.echo()
    click.echo("Linting...")
    lint(workspace=workspace, fix=False, args=())
    click.echo()
    click.echo("Type checking...")
    type_check(workspace=workspace, args=())
    click.echo()
    click.echo("Running coverage (includes tests)...")
    coverage(workspace=workspace, args=())
    click.echo()
    click.echo("All checks passed.")
