from __future__ import annotations

import os
from pathlib import Path

import click

from bygge.constants import IS_WINDOWS
from bygge.workspace import Workspace

from .link_util import discover_scripts, resolve_output_dir


def link(workspace: Workspace, output_dir: Path | None, force: bool) -> None:
    resolved_output_dir = resolve_output_dir(output_dir)
    scripts = discover_scripts(workspace)

    if len(scripts) == 0:
        click.echo("No scripts found in any pyproject.toml")
        return

    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Linking scripts to {resolved_output_dir}:")
    for name, target in sorted(scripts.items()):
        if IS_WINDOWS:
            _install_cmd(name=name, target=target, output_dir=resolved_output_dir, force=force)
        else:
            _install_symlink(name=name, target=target, output_dir=resolved_output_dir, force=force)


def _install_symlink(name: str, target: Path, output_dir: Path, force: bool) -> None:
    link_path = output_dir / name

    if link_path.exists() or link_path.is_symlink():
        if link_path.is_symlink() and Path(os.readlink(link_path)) == target:
            click.echo(f"  {name}: unchanged")
            return
        if not force:
            click.echo(f"  {name}: WARNING - {link_path} already exists and differs, skipping")
            return
        link_path.unlink()

    click.echo(f"  {name}: creating symlink -> {target}")
    link_path.symlink_to(target)


def _install_cmd(name: str, target: Path, output_dir: Path, force: bool) -> None:
    script_path = output_dir / f"{name}.cmd"
    content = f"@echo off\n{target} %*\nexit /b %errorlevel%\n"

    if script_path.exists():
        existing = script_path.read_text()
        if existing == content:
            click.echo(f"  {name}: unchanged")
            return
        if not force:
            click.echo(f"  {name}: WARNING - {script_path} already exists and differs, skipping")
            return

    click.echo(f"  {name}: creating wrapper script -> {target}")
    _ = script_path.write_text(content)
