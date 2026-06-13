from __future__ import annotations

from bygge import ByggeError
from bygge.run import run_subprocess
from bygge.workspace import Workspace


def lint(workspace: Workspace, fix: bool, args: tuple[str, ...]) -> None:
    # TBD: Use plugins instead of hardcoding ruff
    ruff_path = str(workspace.make_bin_path("ruff"))
    target_dir = str(workspace.package_root_dir)
    cmd = [ruff_path, "check", *(["--fix"] if fix else []), target_dir, *args]
    proc = run_subprocess(cmd=cmd, cwd=workspace.workspace_dir, check=False, yes=True)
    if proc.returncode != 0:
        raise ByggeError("Lint check failed")
