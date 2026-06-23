from __future__ import annotations

import os
from pathlib import Path

import click

from bygge import ByggeError
from bygge.constants import IS_WINDOWS
from bygge.workspace import Workspace

from .link_util import discover_scripts, resolve_output_dir


def unlink(workspace: Workspace, output_dir: Path | None) -> None:
    resolved_output_dir = resolve_output_dir(output_dir)

    if not resolved_output_dir.exists():
        raise ByggeError(f"Output directory {resolved_output_dir} does not exist")

    scripts = discover_scripts(workspace)

    if len(scripts) == 0:
        click.echo("No scripts found in any pyproject.toml")
        return

    click.echo(f"Unlinking scripts from {resolved_output_dir}:")
    for name, target in sorted(scripts.items()):
        if IS_WINDOWS:
            _uninstall_cmd(name=name, target=target, output_dir=resolved_output_dir)
        else:
            _uninstall_symlink(name=name, target=target, output_dir=resolved_output_dir)


def _uninstall_symlink(name: str, target: Path, output_dir: Path) -> None:
    link_path = output_dir / name

    if link_path.is_file() or link_path.is_symlink():
        if link_path.is_symlink() and Path(os.readlink(link_path)) == target:
            link_path.unlink()
            click.echo(f"  {name}: removed")
        else:
            click.echo(f"  {name}: WARNING - not installed by bygge, skipping")
    else:
        click.echo(f"  {name}: not found")


def _uninstall_cmd(name: str, target: Path, output_dir: Path) -> None:
    script_path = output_dir / f"{name}.cmd"
    content = f"@echo off\n{target} %*\nexit /b %errorlevel%\n"

    if script_path.is_file():
        existing = script_path.read_text()
        if existing == content:
            script_path.unlink()
            click.echo(f"  {name}: removed")
        else:
            click.echo(f"  {name}: WARNING - not installed by bygge, skipping")
    else:
        click.echo(f"  {name}: not found")
