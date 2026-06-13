from __future__ import annotations

from bygge.run import run_subprocess
from bygge.workspace import Workspace


def commit_unchecked(workspace: Workspace, args: tuple[str, ...]) -> None:
    _ = run_subprocess(
        cmd=["git", "-c", "core.hooksPath=/dev/null", "commit", *args],
        cwd=workspace.workspace_dir,
        check=True,
        yes=True,
    )
