from __future__ import annotations

import click

from bygge.run import run_subprocess
from bygge.workspace import Workspace


def hooks(workspace: Workspace) -> None:
    _ = run_subprocess(
        cmd=["git", "config", "core.hooksPath", "hooks"],
        cwd=workspace.workspace_dir,
        check=True,
        yes=True,
    )
    click.echo("Git hooks installed (using hooks/ directory).")
