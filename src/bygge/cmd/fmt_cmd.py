from __future__ import annotations

from bygge import ByggeError
from bygge.run import run_subprocess
from bygge.workspace import Workspace


def fmt(workspace: Workspace, fix: bool) -> None:
    # TBD: Use plugins instead of hardcoding ruff
    ruff_path = str(workspace.make_bin_path("ruff"))
    target_dir = str(workspace.package_root_dir)

    if fix:
        format_cmd = [ruff_path, "format", target_dir]
        isort_cmd = [ruff_path, "check", "--select", "I", "--fix", target_dir]
    else:
        format_cmd = [ruff_path, "format", "--check", target_dir]
        isort_cmd = [ruff_path, "check", "--select", "I", target_dir]

    proc = run_subprocess(cmd=format_cmd, cwd=workspace.workspace_dir, check=False, yes=True)
    if proc.returncode != 0:
        raise ByggeError("Format check failed")

    proc = run_subprocess(cmd=isort_cmd, cwd=workspace.workspace_dir, check=False, yes=True)
    if proc.returncode != 0:
        raise ByggeError("Import sort check failed")
