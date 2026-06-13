from __future__ import annotations

import sys
from pathlib import Path

import click

from bygge.util import ExecutableInfo
from bygge.workspace import Workspace


def info(workspace: Workspace) -> None:
    info = ExecutableInfo.make()

    click.echo("=== bygge Environment Information ===")
    click.echo()

    # Python executable
    if info.executable_linked:  # pragma: nocover
        click.echo(f"Python executable: {info.executable_unresolved}")
        click.echo(f"  (resolves to: {info.executable_resolved})")
    else:
        click.echo(f"Python executable: {info.executable_resolved}")

    click.echo(f"Python version: {info.python_version}")

    click.echo()

    # bygge invocation
    if info.argv0_linked:  # pragma: no cover
        click.echo(f"Command invoked as: {info.argv0_unresolved}")
        click.echo(f"  (resolves to: {info.argv0_resolved})")
    else:
        click.echo(f"Command invoked as: {info.argv0_resolved}")

    if info.is_python_script:
        click.echo(f"Running as Python script: {info.argv0_resolved}")

    click.echo()

    # Workspace information
    click.echo(f"Current working directory: {workspace.cwd}")
    click.echo(f"Workspace directory: {workspace.workspace_dir}")
    click.echo(f"Package root directory: {workspace.package_root_dir}")
    click.echo(f"Virtual environment directory: {workspace.venv_dir}")
    click.echo()

    # Check if running from project virtual environment using sys.prefix
    # This is more reliable than checking paths because virtual environments use symlinks
    if Path(sys.prefix).resolve() == workspace.venv_dir.resolve():
        click.echo("\u2713 Running from project's virtual environment")
    else:
        click.echo("\u2717 NOT running from project's virtual environment")

    # Also check if the bygge binary itself is from the virtual environment
    try:
        _ = info.argv0_resolved.relative_to(workspace.venv_dir)
        click.echo("\u2713 bygge binary is from project's virtual environment")
    except ValueError:
        click.echo("\u2717 bygge binary is NOT from project's virtual environment")
