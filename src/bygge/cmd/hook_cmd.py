from __future__ import annotations

from pathlib import Path
from string import Template

import click

from bygge import ByggeError
from bygge.run import run_subprocess
from bygge.util.fs import chmod_plus_x
from bygge.workspace import Workspace

_PRE_COMMIT_HOOK_TEMPLATE: Path = (
    Path(__file__).parents[1] / "resources" / "pre-commit-template.txt"
)


def hook(workspace: Workspace, dir: Path | None, create_pre_commit: bool) -> None:
    local_dir = workspace.workspace_dir / "hooks" if dir is None else dir

    try:
        repo_path = local_dir.relative_to(workspace.workspace_dir).as_posix()
    except ValueError as e:  # pragma: no cover
        raise ByggeError(f"{local_dir} is not in subpath of {workspace.workspace_dir}") from e

    _ = run_subprocess(
        cmd=["git", "config", "core.hooksPath", repo_path],
        cwd=workspace.workspace_dir,
        check=True,
        yes=True,
    )
    click.echo(f"Git hooks installed into {repo_path} directory")

    if create_pre_commit:
        venv_rel_path = workspace.venv_dir.relative_to(workspace.workspace_dir).as_posix()

        pre_commit_path = local_dir / "pre-commit"
        if pre_commit_path.is_file():
            raise ByggeError(f"Pre-commit hook file {pre_commit_path} already exists")

        template = Template(_PRE_COMMIT_HOOK_TEMPLATE.read_text())
        s = template.substitute({"VENV_DIR": venv_rel_path})

        _ = pre_commit_path.write_text(s)
        chmod_plus_x(pre_commit_path)
        _ = run_subprocess(
            cmd=["git", "add", "--chmod=+x", "--", pre_commit_path.as_posix()],
            cwd=workspace.workspace_dir,
            check=True,
            yes=True,
        )

        click.echo(f"Git pre-commit hook installed to {pre_commit_path}")
