from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, override

import click
from click import Context, Group, argument, option, pass_context, pass_obj

from bygge import ByggeError
from bygge.cmd import (
    check,
    commit_unchecked,
    coverage,
    fmt,
    hooks,
    info,
    init,
    lint,
    recode,
    test,
    type_check,
    unhook,
)
from bygge.constants import IS_WINDOWS
from bygge.run import run_subprocess
from bygge.util import (
    ARGS_ARG,
    CWD_OPT,
    WORKSPACE_DIR_OPT,
    YES_OPT,
    ColourFormatter,
    ExecutableInfo,
)
from bygge.util.cli import UNKNOWN_ARGS_CTX, NamedChoice
from bygge.util.env import env_truthy
from bygge.workspace import Workspace

logger = logging.getLogger(__name__)


def _log_executable_info() -> None:
    """Log information about the currently running executable."""

    info = ExecutableInfo.make()

    # Log both the symlink and its target if they differ
    if info.executable_linked:  # pragma: nocover
        logger.debug(
            f"Python executable: {info.executable_unresolved} -> {info.executable_resolved}"
        )
    else:  # pragma: no cover
        logger.debug(f"Python executable: {info.executable_resolved}")

    logger.debug(f"Python version: {info.python_version}")

    if info.argv0_linked:  # pragma: no cover
        logger.debug(f"Command invoked as: {info.argv0_unresolved} -> {info.argv0_resolved}")
    else:
        logger.debug(f"Command invoked as: {info.argv0_resolved}")

    if info.is_python_script:
        logger.debug(f"Running as Python script: {info.argv0_resolved}")


def _is_running_from_project_venv(workspace: Workspace) -> bool:
    """Check if the current Python process is from the project's virtual environment."""
    # Use sys.prefix - Python sets this to the venv directory when a venv is active
    # This is more reliable than checking sys.executable, which resolves symlinks
    return Path(sys.prefix).resolve() == workspace.venv_dir.resolve()


def _get_delegate_venv_bygge_path(workspace: Workspace) -> Path | None:
    """
    Determine if we should delegate to the project's venv bygge.

    Returns True if:
    - A venv exists for the project
    - We're NOT already running from that venv
    - The venv has a bygge binary
    """
    venv_dir = workspace.venv_dir

    # Check if venv exists
    if not venv_dir.exists():
        logger.debug("No virtual environment found, continuing with current bygge")
        return None

    # Check if we're already running from the project venv
    if _is_running_from_project_venv(workspace):  # pragma: no cover
        logger.debug("Already running from project's virtual environment")
        return None

    # Check if project venv has bygge binary
    venv_bygge_path = (
        venv_dir / "Scripts" / "bygge.exe" if IS_WINDOWS else venv_dir / "bin" / "bygge"
    )
    if venv_bygge_path.is_file():  # pragma: nocover
        return venv_bygge_path

    logger.warning(
        f"Project virtual environment exists but bygge not found at {venv_bygge_path}. "
        + "Continuing with current bygge instance."
    )
    return None


def _delegate_to_venv_bygge(
    workspace: Workspace, venv_bygge_path: Path
) -> None:  # pragma: no cover
    """Execute the project's venv bygge with the same arguments."""
    t0 = (
        workspace.venv_dir / "Scripts" / "bygge.exe"
        if IS_WINDOWS
        else workspace.venv_dir / "bin" / "bygge"
    )
    assert t0 == venv_bygge_path

    if IS_WINDOWS:
        proc = run_subprocess(
            [str(venv_bygge_path), *sys.argv[1:]], cwd=Path.cwd(), check=False, yes=True
        )
        sys.exit(proc.returncode)
    else:
        # Reconstruct the command line, skipping argv[0] (which is the current bygge)
        args = [str(venv_bygge_path), *sys.argv[1:]]

        logger.debug(f"Delegating to: {' '.join(args)}")

        # Execute and exit with the same code
        os.execv(str(venv_bygge_path), args)


class ByggeGroup(Group):
    @override
    def parse_args(self, ctx: Context, args: list[str]) -> list[str]:
        """
        Reorder args to allow group-level options after the subcommand.

        Examples:
            bygge info --level debug  \u2192  bygge --level debug info
            bygge test --level debug  \u2192  bygge --level debug test
        """
        # Collect known option names for this group
        opt_names = set[str]()
        for param in self.params:
            opt_names.update(param.opts)
            opt_names.update(param.secondary_opts)

        # Scan args: once we see a subcommand, move any group-level options to the front
        pre_args: list[str] = []
        post_args: list[str] = []
        i = 0
        found_subcommand = False

        while i < len(args):
            arg = args[i]
            if not found_subcommand and arg in self.commands:
                found_subcommand = True
                post_args.append(arg)
                i += 1
            elif found_subcommand and arg in opt_names:
                pre_args.append(arg)
                i += 1
                # If the option takes a value, grab the next arg too
                for param in self.params:
                    if arg in param.opts or arg in param.secondary_opts:
                        # Use getattr because is_flag exists but isn't in Click's type stubs
                        if not getattr(param, "is_flag", False) and i < len(args):
                            pre_args.append(args[i])
                            i += 1
                        break
            else:
                if found_subcommand:  # pragma: no cover
                    post_args.append(arg)
                else:
                    pre_args.append(arg)
                i += 1

        return super().parse_args(ctx, pre_args + post_args)

    @override
    def invoke(self, ctx: Context) -> Any:  # pyright: ignore[reportAny, reportExplicitAny]
        try:
            return super().invoke(ctx)  # pyright: ignore[reportAny]
        except ByggeError as e:
            raise click.ClickException(str(e)) from e


@click.group(cls=ByggeGroup)
@pass_context
@CWD_OPT
@WORKSPACE_DIR_OPT
@option(
    "--level",
    type=NamedChoice(
        [
            (s, getattr(logging, s.upper()))
            for s in ["debug", "info", "warning", "error", "critical"]
        ]
    ),
    default="info",
)
@option(
    "--do-not-delegate", is_flag=True, default=env_truthy("BYGGE_DO_NOT_DELEGATE", default=False)
)
def main(
    ctx: Context, cwd: Path, workspace_dir: Path | None, level: int, do_not_delegate: bool
) -> None:  # pragma: no cover
    logging.basicConfig(level=level)
    handler = logging.getLogger().handlers[0]
    handler.setFormatter(ColourFormatter("[%(levelname)s] %(message)s"))

    # Log executable information
    _log_executable_info()

    # Find workspace (may not exist for init command)
    workspace: Workspace | None = None
    try:
        workspace = Workspace.find(cwd=cwd, workspace_dir=workspace_dir)
    except click.ClickException as e:
        # No workspace found - store the exception to re-raise later if needed
        if ctx.invoked_subcommand != "init":
            # For non-init commands, workspace is required
            raise
        # For init command, workspace not being found is acceptable
        logger.debug(f"No workspace found: {e}")

    # Check delegation and warnings
    if workspace and ctx.invoked_subcommand:
        if ctx.invoked_subcommand == "init":
            # Warn if running init from project's own venv
            if _is_running_from_project_venv(workspace):
                logger.warning(
                    "Running 'init' from the project's own virtual environment. "
                    + "Consider using a global or external bygge installation for bootstrapping."
                )
        else:
            # For non-init commands, check if we should delegate to venv bygge
            if (venv_bygge_path := _get_delegate_venv_bygge_path(workspace)) is not None:
                if do_not_delegate:
                    logger.warning("--do-not-delegate was passed so we'll keep using this bygge")
                else:
                    logger.warning(
                        "Running bygge from outside project's virtual environment. "
                        + f"Delegating to {venv_bygge_path}"
                    )
                    _delegate_to_venv_bygge(workspace=workspace, venv_bygge_path=venv_bygge_path)

    ctx.obj = workspace


@main.command("init", help="Set up the development environment")
@pass_obj
@option("--reinit/--no-reinit", type=bool, is_flag=True, default=False)
@option("--install/--no-install", type=bool, is_flag=True, default=True)
@YES_OPT
def init_cmd(
    workspace: Workspace, reinit: bool, install: bool, yes: bool
) -> None:  # pragma: no cover
    init(workspace=workspace, reinit=reinit, install=install, yes=yes)


@main.command("info", help="Display environment information")
@pass_obj
def info_cmd(workspace: Workspace) -> None:  # pragma: no cover
    info(workspace=workspace)


@main.command("test", help="Run tests", context_settings=UNKNOWN_ARGS_CTX)
@pass_obj
@ARGS_ARG
def test_cmd(workspace: Workspace, args: tuple[str, ...]) -> None:  # pragma: no cover
    test(workspace=workspace, args=args)


@main.command("coverage", help="Run tests with code coverage", context_settings=UNKNOWN_ARGS_CTX)
@pass_obj
@ARGS_ARG
def coverage_cmd(workspace: Workspace, args: tuple[str, ...]) -> None:  # pragma: no cover
    coverage(workspace=workspace, args=args)


@main.command("fmt", help="Format code and sort imports")
@pass_obj
@option("--fix/--check", type=bool, is_flag=True, default=False)
def fmt_cmd(workspace: Workspace, fix: bool) -> None:  # pragma: no cover
    fmt(workspace=workspace, fix=fix)


@main.command("lint", help="Run linting and optional fix issues", context_settings=UNKNOWN_ARGS_CTX)
@pass_obj
@ARGS_ARG
@option("--fix/--check", type=bool, is_flag=True, default=False)
def lint_cmd(workspace: Workspace, fix: bool, args: tuple[str, ...]) -> None:  # pragma: no cover
    lint(workspace=workspace, fix=fix, args=args)


@main.command("check", help="Run all pre-commit checks")
@pass_obj
def check_cmd(workspace: Workspace) -> None:  # pragma: no cover
    check(workspace=workspace)


@main.command("typecheck", help="Type-check source code", context_settings=UNKNOWN_ARGS_CTX)
@pass_obj
@ARGS_ARG
def type_check_cmd(workspace: Workspace, args: tuple[str, ...]) -> None:  # pragma: no cover
    type_check(workspace=workspace, args=args)


@main.command("hooks", help="Install Git pre-commit hook")
@pass_obj
def hooks_cmd(workspace: Workspace) -> None:  # pragma: no cover
    hooks(workspace=workspace)


@main.command("unhook", help="Uninstall Git pre-commit hook")
@pass_obj
def unhook_cmd(workspace: Workspace) -> None:  # pragma: no cover
    unhook(workspace=workspace)


@main.command(
    "commit-unchecked", help="Commit bypassing pre-commit hook", context_settings=UNKNOWN_ARGS_CTX
)
@pass_obj
@ARGS_ARG
def commit_unchecked_cmd(workspace: Workspace, args: tuple[str, ...]) -> None:  # pragma: no cover
    commit_unchecked(workspace=workspace, args=args)


@main.command(
    "recode", help="Convert non-ASCII characters in Python source files to Unicode escape sequences"
)
@argument(
    "path",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, writable=True, resolve_path=True, path_type=Path
    ),
    required=True,
)
def recode_cmd(path: Path) -> None:  # pragma: no cover
    recode(path=path)
