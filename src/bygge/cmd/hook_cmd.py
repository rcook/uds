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
    hook_dir = workspace.workspace_dir / "hooks" if dir is None else dir

    try:
        hook_rel_path = hook_dir.relative_to(workspace.workspace_dir)
    except ValueError as e:  # pragma: no cover
        raise ByggeError(f"{hook_dir} is not in subpath of {workspace.workspace_dir}") from e

    _ = run_subprocess(
        cmd=["git", "config", "core.hooksPath", hook_rel_path.as_posix()],
        cwd=workspace.workspace_dir,
        check=True,
        yes=True,
    )
    click.echo(f"Git hooks installed into {hook_dir} directory")

    if not hook_dir.is_dir() and not create_pre_commit:  # pragma: no cover
        click.echo(
            f"WARNING: Directory {hook_dir} does not exist yet: "
            + "pass --create-pre-commit to create directory with pre-commit hook"
        )

    if create_pre_commit:
        venv_rel_path = workspace.venv_dir.relative_to(workspace.workspace_dir).as_posix()

        hook_dir.mkdir(parents=True, exist_ok=True)

        pre_commit_path = hook_dir / "pre-commit"
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
