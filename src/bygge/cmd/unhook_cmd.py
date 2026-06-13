from __future__ import annotations

import click

from bygge.run import run_subprocess
from bygge.workspace import Workspace


def unhook(workspace: Workspace) -> None:
    _ = run_subprocess(
        cmd=["git", "config", "--unset", "core.hooksPath"],
        cwd=workspace.workspace_dir,
        check=True,
        yes=True,
    )
    click.echo("Git hooks uninstalled (restored to default .git/hooks).")
